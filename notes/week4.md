
### Observed v1 results

| Item | v1 result |
|---|---|
| Image disk usage | 269 MB |
| Image content size | 64.1 MB |
| `docker history` rows | 15 history entries (includes base-image history) |
| Runtime user | `uid=0(root) gid=0(root) groups=0(root)` |
| `pip` | Present: `/usr/local/bin/pip` |
| `gcc`, `curl`, `git` | Not found |
| Trivy HIGH | 49 |
| Trivy CRITICAL | 0 |
| Python package vulnerabilities | 0 reported |

The largest application-related history layer was the dependency installation layer (`RUN pip install --no-cache-dir -r requirements.txt`), shown as 71.1 MB in `docker history`.


### Observed timings after the code change

| Build | Real time |
|---|---:|
| `Dockerfile.slow` | 48.119 seconds |
| Original v1 `Dockerfile` | 3.509 seconds |

**Conclusion:** The original Dockerfile rebuilt much faster (about 13.7 times faster in this run). It copies `requirements.txt` and installs dependencies before copying the application code. A change limited to `app/main.py` therefore leaves the dependency layer cached. In `Dockerfile.slow`, `COPY . .` happens before dependency installation, so the code change invalidates the later install layer.


## 7. Week 4 questions — draft answers

**1. Compare v1 and v2. Which change gives the biggest size difference and which gives the biggest security difference?**

Use the measured v2 results to make the comparison. The multi-stage build and production-only requirements reduce what is included in the final image. The non-root `USER 10001` is a major security improvement because a compromised application no longer immediately has root privileges. The read-only filesystem, dropped capabilities, no-new-privileges setting, and resource limits add further defense in depth.

**2. Which build was faster after the code change, and which line explains it?**

The original v1 Dockerfile was faster: 3.509 seconds versus 48.119 seconds for `Dockerfile.slow`. The key ordering is `COPY requirements.txt .` followed by `RUN pip install ...`, before `COPY app ./app`. This allows Docker to reuse the dependency layer when only application code changes.

**3. Why did `RUN rm fake-config.txt` not remove the secret? What should the team do first after a real key was pushed?**

The file was stored in an earlier immutable image layer by `COPY`. The later `RUN rm` only adds a deletion in a newer layer; it does not erase the earlier layer's contents. A real exposed key must be revoked/rotated immediately and replaced, then the team should investigate the exposure.

**4. Why scan a saved `.tar` instead of mounting `/var/run/docker.sock` into Trivy?**

Scanning the exported image archive lets Trivy inspect the image without access to the Docker daemon socket. The Docker socket is highly privileged: a process with access may control the Docker daemon and potentially gain host-level control. Avoiding the socket reduces the scanner container's privileges.

**5. Pick one HIGH finding from v2. Is a fixed version available, and what would you change?**

**Pending:** choose an actual HIGH finding from your v2 Trivy output (or v1 if v2 has none). Check the finding's fixed version in the scan report. Do not invent a package or fixed version. If a fixed version is available, update the relevant base image or dependency to a version containing the fix, rebuild, and rescan.

**6. D1 failed and D2 worked. Why do we want both behaviors?**

The application should not be able to modify its own code or the container's root filesystem, limiting persistence after compromise. It still needs a designated writable temporary location for runtime operations, so `/tmp` is mounted separately as writable tmpfs.

**7. Why was `docker stop` fast? What might happen with shell-form CMD?**

With exec-form CMD, Docker starts Uvicorn directly as PID 1, so it receives the termination signal and can shut down gracefully. With shell-form CMD, a shell may become PID 1 and not forward the signal properly to Uvicorn; shutdown may be delayed until Docker's timeout and forced termination.
