# react-frontend
A sample react frontend

## Prerequisites
- nix shell installed locally (or install nodejs otherwise)
- syft installed ([install instructions](https://github.com/anchore/syft?tab=readme-ov-file#installation))

## Run in dev mode with dependencies

```bash
# Start nix shell with nodejs
nix-shell -p nodejs

# Install dependencies
npm install

# Run in dev mode
npm run dev
```

## Build docker image and run react in docker
Do the following to build the docker image and run the sample react frontend in the docker container.

```bash
# Build the image
docker build -t react-frontend .

# Run the container
docker run -p 3000:80 react-frontend
```

Now visit [http://localhost:3000/](http://localhost:3000/) to see the app running.

## Run syft scans
Run the following commands to scan the project with syft.

```bash
# Create CyclonDX SBOM from project root
syft ./ -o cyclonedx-json > sbom/cyclonedx.json

```


## React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

### Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
