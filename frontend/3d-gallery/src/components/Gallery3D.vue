<template>
  <div ref="canvasContainer" class="gallery-container"></div>
</template>

<script>
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { GUI } from "three/examples/jsm/libs/lil-gui.module.min.js";

export default {
  mounted() {
    const container = this.$refs.canvasContainer;

    // Creating a scene, camera and rendering
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      container.clientWidth / container.clientHeight,
      0.1,
      1000
    );
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    // Using Tone Mapping to correct brightness and contrast
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;

    // Loading a texture
    const textureLoader = new THREE.TextureLoader();
    const urlParams = new URLSearchParams(window.location.search);
    const imageUrl = urlParams.get("image") || "/images/default.jpg";

    textureLoader.load(decodeURIComponent(imageUrl), (texture) => {
      // Get the real size of the image
      const imageAspect = texture.image.width / texture.image.height;

      // Determine the width and height of the canvas in accordance with the proportions
      let planeWidth = 5; // Base width
      let planeHeight = planeWidth / imageAspect; // Calculate the height

      // Creating a material (MeshStandardMaterial)
      const material = new THREE.MeshStandardMaterial({ map: texture });

      // Create geometry with the right proportions
      const geometry = new THREE.PlaneGeometry(planeWidth, planeHeight);
      const plane = new THREE.Mesh(geometry, material);

      scene.add(plane);
    });

    // Adding OrbitControls for a limited view
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.minDistance = 0.3; // Minimum distance to the picture
    controls.maxDistance = 7; // Maximum distance
    controls.enablePan = false; // Disable panning

    // Turn circle restriction (only frontal view)
    controls.minPolarAngle = Math.PI / 6;   // ≈ 30° (from above)
    controls.maxPolarAngle = Math.PI / 1.2; // ≈ 150° (bottom)

    controls.minAzimuthAngle = -Math.PI / 2.2; // ≈ -90° (left)
    controls.maxAzimuthAngle = Math.PI / 2.2;  // ≈ 90° (right)

    // Setting up the camera for the first time
    camera.position.set(0, 0, 5);

    // Add a background with a light gradient
    const backgroundTexture = new THREE.TextureLoader().load("/images/background.jpg");
    scene.background = backgroundTexture;

    // Add light only for effect (NOT for the picture)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.2); // Reduce the intensity
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 1.5, 50);
    pointLight.position.set(0, 5, 5);
    scene.add(pointLight);

    // Adding a GUI for light control
    const gui = new GUI();
    const lightFolder = gui.addFolder("Освітлення");
    lightFolder.add(ambientLight, "intensity", 0, 2, 0.1).name("Ambient Light");
    lightFolder.add(pointLight, "intensity", 0, 3, 0.1).name("Point Light");
    lightFolder.add(pointLight.position, "x", -10, 10, 0.1).name("Light X");
    lightFolder.add(pointLight.position, "y", -10, 10, 0.1).name("Light Y");
    lightFolder.add(pointLight.position, "z", -10, 10, 0.1).name("Light Z");
    lightFolder.open();

    // Animation cycle
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();
  }
};
</script>

<style>
.gallery-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>
