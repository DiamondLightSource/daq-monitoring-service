[![CI](https://github.com/DiamondLightSource/daq-monitoring-service/actions/workflows/ci.yml/badge.svg)](https://github.com/DiamondLightSource/daq-monitoring-service/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/DiamondLightSource/daq-monitoring-service/branch/main/graph/badge.svg)](https://codecov.io/gh/DiamondLightSource/daq-monitoring-service)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# daq_monitoring_service

Monitors primarily DAQ things and informs beamline staff when they change

This is where you should write a short paragraph that describes what your module does,
how it does it, and why people should use it.

What            | Where
:---:           | :---:
Source          | <https://github.com/DiamondLightSource/daq-monitoring-service>
Docker          | `docker run ghcr.io/diamondlightsource/daq-monitoring-service:latest`
Releases        | <https://github.com/DiamondLightSource/daq-monitoring-service/releases>

This is where you should put some images or code snippets that illustrate
some relevant examples. If it is a library then you might put some
introductory code here:

```python
from daq_monitoring_service import __version__

print(f"Hello daq_monitoring_service {__version__}")
```

Or if it is a commandline tool then you might put some example commands here:

```
python -m daq_monitoring_service --version
```

## Containers and Kubernetes deployment

Run these commands from the repository root. You need Podman for local builds,
and Helm and `kubectl` configured for the target cluster to deploy. The cluster
must already have the Sealed Secrets CRD and controller installed.

### Build, run and push locally

The build script creates a local `daq-monitoring-service:dev` image by default.
It reuses that image on subsequent runs; use `--rebuild` after changing code.
Invoke the options separately (the script does not reliably parse combinations
of options):

```sh
bash deployment/build_and_push.sh --rebuild
bash deployment/build_and_push.sh --run
```

`--run` starts a detached local container named `daq-monitoring-service` and
replaces an existing container of that name. To publish the local `dev` image
to GHCR, authenticate with Podman first, then pass the registry **prefix**
(including the trailing `/`) to `--push`:

```sh
podman login ghcr.io
bash deployment/build_and_push.sh --push ghcr.io/diamondlightsource/
```

This pushes `ghcr.io/diamondlightsource/daq-monitoring-service:dev`. You need
permission to push to that registry; substitute another prefix if necessary.
The script's `--run` does not provide credentials or configuration to the
container; it is not a substitute for the Kubernetes deployment.

### Deploy a release with Helm

**In general, deploy an image produced from a project release**, not a locally
built `dev` image. Choose an existing published release image tag and set the
chart's image tag to match it. The bundled SealedSecret is sealed for the Secret
name `daq-monitoring-service-secrets` in namespace `daq-monitoring-service`
and the cluster whose controller key was used to seal it; it cannot simply be
installed in another namespace or cluster. The Deployment reads that Secret
via `envFromSecret`.

```sh
RELEASE_TAG=v0.1.0  # replace with a tag actually published for a release
helm upgrade --install daq-monitoring-service ./helm/daq-monitoring-service \
	--namespace daq-monitoring-service \
	--set-string image.repository=ghcr.io/diamondlightsource/daq-monitoring-service \
	--set-string image.tag="$RELEASE_TAG"
kubectl -n daq-monitoring-service get deployments,pods,sealedsecrets,secrets
```
