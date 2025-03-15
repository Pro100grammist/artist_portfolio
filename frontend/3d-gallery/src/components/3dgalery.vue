


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

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      container.clientWidth / container.clientHeight,
      0.1,
      100
    );
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 1.5, 30);
    pointLight.position.set(0, 2.5, 3);
    scene.add(pointLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(-5, 5, 5);
    scene.add(directionalLight);

    const textureLoader = new THREE.TextureLoader();
    const urlParams = new URLSearchParams(window.location.search);
    const imageUrl = urlParams.get("image") || "/images/default.jpg";
    const texture = textureLoader.load(decodeURIComponent(imageUrl));

    const pictureWidth = 2;
    const pictureHeight = 1.5;

    const material = new THREE.MeshStandardMaterial({ map: texture });
    const picture = new THREE.Mesh(
      new THREE.PlaneGeometry(pictureWidth, pictureHeight),
      material
    );
    picture.position.set(0, 1.6, -3.5);
    scene.add(picture);

    const frameMaterial = new THREE.MeshStandardMaterial({ color: 0x8b5a2b });
    const frameThickness = 0.1;
    const frameDepth = 0.05;

    const createFramePart = (width, height, x, y, z) => {
      const part = new THREE.Mesh(
        new THREE.BoxGeometry(width, height, frameDepth),
        frameMaterial
      );
      part.position.set(x, y, z);
      scene.add(part);
    };

    // Коригування розташування рамки
    createFramePart(pictureWidth + frameThickness, frameThickness, 0, 1.6 + pictureHeight / 2 + frameThickness / 2, -3.45); // Верхня рамка
    createFramePart(pictureWidth + frameThickness, frameThickness, 0, 1.6 - pictureHeight / 2 - frameThickness / 2, -3.45); // Нижня рамка
    createFramePart(frameThickness, pictureHeight, -pictureWidth / 2 - frameThickness / 2, 1.6, -3.45); // Ліва рамка
    createFramePart(frameThickness, pictureHeight, pictureWidth / 2 + frameThickness / 2, 1.6, -3.45); // Права рамка

    const roomWidth = 6;
    const roomHeight = 4;
    const roomDepth = 8;

    const wallTexture = textureLoader.load("/images/wall-texture.jpg");
    const floorTexture = textureLoader.load("/images/floor-texture.jpg");
    const ceilingTexture = textureLoader.load("/images/ceiling-texture.jpg");

    const createWall = (width, height, depth, x, y, z, texture) => {
      const material = new THREE.MeshBasicMaterial({ map: texture });
      const wall = new THREE.Mesh(
        new THREE.BoxGeometry(width, height, depth),
        material
      );
      wall.position.set(x, y, z);
      scene.add(wall);
    };

    createWall(roomWidth, roomHeight, 0.1, 0, roomHeight / 2, -4, wallTexture);
    createWall(0.1, roomHeight, roomDepth, -roomWidth / 2, roomHeight / 2, 0, wallTexture);
    createWall(0.1, roomHeight, roomDepth, roomWidth / 2, roomHeight / 2, 0, wallTexture);
    createWall(roomWidth, 0.1, roomDepth, 0, roomHeight, 0, ceilingTexture);
    createWall(roomWidth, 0.1, roomDepth, 0, 0, 0, floorTexture);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    camera.position.set(0, 1.6, -3);

    controls.minPolarAngle = 0;
    controls.maxPolarAngle = Math.PI;
    controls.minAzimuthAngle = -Infinity;
    controls.maxAzimuthAngle = Infinity;
    controls.enablePan = true;

    const gui = new GUI();
    const lightFolder = gui.addFolder("Освітлення");
    lightFolder.add(pointLight, "intensity", 0, 2).name("Лампочка");
    lightFolder.add(directionalLight, "intensity", 0, 2).name("Сонячне світло");
    lightFolder.add(ambientLight, "intensity", 0, 2).name("Фонове світло");
    lightFolder.open();
    
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();
  },
};
</script>

<style>
.gallery-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>
