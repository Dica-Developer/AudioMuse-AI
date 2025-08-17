# Contributing to AudioMuse-AI

Thank you for considering a contribution to AudioMuse-AI. Open-source projects thrive on the collective effort and expertise of their communities, and every contribution, regardless of size, is highly valued.

The vision of AudioMuse-AI is to bring Sonic Analysis open and free to the higher number of user possible. So each change should aim to bring it more usebul from more and more users.

The project is currently in a BETA release stage. This means there is a wealth of opportunity to make a significant and lasting impact. Whether it involves fixing a bug, implementing a new feature, or improving the documentation, your contributions are essential to the project's growth and stability.

Remember that contributing not only means develop code, also suggest new feature, highlight a bug or just share your feedback (good or bad is always important) by an [issue](https://github.com/NeptuneHub/AudioMuse-AI/issues) is also contributing.

## High-Level Architecture
To contribute effectively, it is crucial to understand that AudioMuse-AI is not a monolithic program. It is a multi-service, containerized application designed for robustness, scalability, and a clear separation of concerns. This architecture is composed of several core components that work in concert.
* **Flask Web Application (audiomuse-ai-flask):** Here you have the front-end of the application both intended as html page and API. Here live also the logic of the service that are syncronous like get the similar song.
* **Redis Queue (RQ) Workers (audiomuse-ai-worker):** This is for what need to be executed in async, like analyze the song, do clustering or reconstruct the index for similar song search. With the redis queue and a kubernetes architecture is possible to spawn more woker for increase scalability and avaiability.
* **PostgreSQL Database (postgres-deployment):** The database. Not only the analysis live here but also the log status o the async task.

 ## Supported Architecture and Mediaserver

 Remember that this software support both Intel and Arm architecture. So avoid code that will not work on both except for very specific case. If you're not able to test on both architecture, add this in the PR description.

 Rememeber also that this application support multiple mediaserver, at the moment Jellyfin and Navidrome. So try to don't introduce change that can distrupt one or the other mediaserver. If you're not able to test on all mediaserver, add this in the PR description.

## **The Codebase Map**

The following table details the most important paths in the repository, their purpose, and the key technologies associated with them.

| Path | Purpose |
| :---- | :---- |
| app.py, app_*.py | The main entry point for the Flask web application. It handles the initialization of the Flask app, database connections, and the registration of API routes and blueprints. |
| tasks/ | **The Core Logic Hub.** This is where the most intensive computations occur. Each API or async task then point to an specific implementation in this directory|
| tasks/mediaserver.py | In this fail the generic method to interact with the mediaservers are specialized to call the specific one |
| ai.py | This module centralizes all interactions with Large Language Models (LLMs). It contains the logic for communicating with services like self-hosted Ollama or the Google Gemini API for tasks such as AI-powered playlist naming and translating natural language requests into SQL queries. |
| config.py | Contains the application's default, non-sensitive configuration parameters. These values serve as fallbacks and can be easily overridden by environment variables, providing a flexible and secure configuration system. |
| static/ & templates/ | These directories contain all frontend assets. |
| deployment/ | This contains deployment example but also the supervisord configuration |
| Dockerfile, Dockerfile.nvidia | These files contain the instructions for building the OCI-compatible container images for the application. |
| .github/ | This directory holds GitHub-specific configuration files, such as issue templates, pull request templates, and potentially continuous integration/continuous deployment (CI/CD) workflows.1 |

## **Prerequisites**

The development environment for AudioMuse-AI is fully containerized to ensure consistency and simplify setup. The only required tools are:

* **Git:** For version control and interacting with the GitHub repository.  
* **Docker and Docker Compose:** For building and running the containerized application stack.

Because the entire application runs inside Docker containers, there is no need to install Python, PostgreSQL, or Redis directly on the local development machine.

## **How to compile**

If you have a k3s (kubernetes) cluster at home, I highly recommend to deploy a local registry and then directly deploy the image against it. To do that I suggest to follow my [private-registry how-to](https://github.com/NeptuneHub/k3s-supreme-waffle/tree/main/private-registry)

If you don't have K3s (kubernetes) at home, you can just use docker-compose to compile the `docker-compose.yaml` file on the flight. Remember to point it to your local image by changing this:

```
audiomuse-ai-flask:
    image: ghcr.io/neptunehub/audiomuse-ai:0.6.5-beta
    # ... rest of the service definition
```

to something like this:
```
audiomuse-ai-flask:
    build:
      context: .  # <-- ADD THIS: Tells Docker to look for the Dockerfile in the current directory
      dockerfile: Dockerfile # <-- ADD THIS: Specifies the name of the Dockerfile
    image: audiomuse-ai:dev # <-- CHANGE THIS: Give your local build a new, clear name
    # ... rest of the service definition
```

for both `flask` and `worker` container. Then you can just run&build with this command:

```
docker-compose up --build -d
```

## **PR**

When you find something on which you would like to work you can fork the repository and start working on. When then you open a PR to be merged is important that:

* You describe clearly what do you want to achive with thi;
* The code is tested on the main feature to avoid regression on at least one architecture and one mediaserver, where main feature in this moment are:
  * Analysis and Clustering,  Instant Playlist, Playlist from Similar Song, Song Path and Sonic Fingerprint (basicaly reach the integrated front-end and do at least 1 test for each function in the meny)
* The code that you bring is alligned with the actual license of AudioMuse-AI

It's also useful if you check for other open PR to look if there is someoneelse working on the same feature. For long implementation is useful if you create the PR as a Draft from the beginning to give visibility from other user.

##  **Related Repositories** 
  > * [AudioMuse-AI](https://github.com/NeptuneHub/AudioMuse-AI): the core application, it run Flask and Worker containers to actually run all the feature;
  > * [AudioMuse-AI Helm Chart](https://github.com/NeptuneHub/AudioMuse-AI-helm): helm chart for easy installation on Kubernetes;
  > * [AudioMuse-AI Plugin for Jellyfin](https://github.com/NeptuneHub/audiomuse-ai-plugin): Jellyfin Plugin.


## **Questions**

For any question you can [raise an issue](https://github.com/NeptuneHub/AudioMuse-AI/issues)

