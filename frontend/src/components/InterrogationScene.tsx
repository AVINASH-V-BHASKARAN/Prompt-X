/** @jsxImportSource @/lib/three-jsx */
import { useMemo } from "react";
import * as THREE from "three";

function texture(seed: number, base: string, fleck: string, repeat: [number, number]) {
  const canvas = document.createElement("canvas");
  canvas.width = 96;
  canvas.height = 96;
  const context = canvas.getContext("2d");
  if (!context) return new THREE.Texture();

  context.fillStyle = base;
  context.fillRect(0, 0, 96, 96);
  let value = seed;
  for (let index = 0; index < 440; index += 1) {
    value = (value * 9301 + 49297) % 233280;
    const x = (value / 233280) * 96;
    value = (value * 9301 + 49297) % 233280;
    const y = (value / 233280) * 96;
    context.globalAlpha = 0.12 + (index % 5) * 0.035;
    context.fillStyle = fleck;
    context.fillRect(x, y, 1 + (index % 3), 1);
  }
  context.globalAlpha = 1;
  const result = new THREE.CanvasTexture(canvas);
  result.wrapS = result.wrapT = THREE.RepeatWrapping;
  result.repeat.set(...repeat);
  result.magFilter = THREE.NearestFilter;
  result.minFilter = THREE.NearestFilter;
  return result;
}

function FilingCabinet() {
  return (
    <group position={[3.55, -1.5, -0.15]}>
      <mesh castShadow>
        <boxGeometry args={[1.25, 2.4, 1.05]} />
        <meshStandardMaterial color="#403b32" roughness={0.78} metalness={0.25} />
      </mesh>
      {[-0.7, 0, 0.7].map((y) => (
        <group key={y} position={[0, y, 0.535]}>
          <mesh>
            <boxGeometry args={[1.05, 0.05, 0.035]} />
            <meshStandardMaterial color="#171815" />
          </mesh>
          <mesh position={[0, -0.2, 0.04]}>
            <boxGeometry args={[0.28, 0.08, 0.05]} />
            <meshStandardMaterial color="#161612" metalness={0.5} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

export function InterrogationScene() {
  const wallTexture = useMemo(() => texture(71, "#29251f", "#655441", [8, 5]), []);
  const deskTexture = useMemo(() => texture(19, "#624637", "#bb8b67", [6, 3]), []);
  const floorTexture = useMemo(() => texture(37, "#241f19", "#69503a", [9, 8]), []);

  return (
    <>
      <color attach="background" args={["#0a0a08"]} />
      <fog attach="fog" args={["#0a0a08", 7, 19]} />
      <ambientLight intensity={0.38} color="#a49b83" />
      <pointLight position={[0, 4.6, 2]} color="#f5bd6b" intensity={45} distance={10} decay={2} castShadow shadow-mapSize-width={1024} shadow-mapSize-height={1024} />
      <spotLight position={[0, 5.4, 1.5]} target-position={[0, 0, 0]} color="#f5c98b" intensity={70} angle={0.5} penumbra={0.45} castShadow />
      <mesh position={[0, 1.1, -3]} receiveShadow>
        <boxGeometry args={[11, 7.3, 0.28]} />
        <meshStandardMaterial map={wallTexture} roughness={1} />
      </mesh>
      <mesh position={[0, -2.62, 0]} rotation-x={-Math.PI / 2} receiveShadow>
        <planeGeometry args={[12, 10]} />
        <meshStandardMaterial map={floorTexture} roughness={1} />
      </mesh>

      <group position={[0, 1.1, -2.78]}>
        <mesh>
          <boxGeometry args={[4.9, 2.75, 0.18]} />
          <meshStandardMaterial color="#171a18" roughness={0.7} metalness={0.3} />
        </mesh>
        <mesh position={[0, 0, 0.11]}>
          <planeGeometry args={[4.32, 2.22]} />
          <meshStandardMaterial color="#30352f" roughness={0.28} metalness={0.45} />
        </mesh>
        {[-0.65, -0.3, 0.05, 0.4, 0.75].map((y) => (
          <mesh key={y} position={[0, y, 0.125]}>
            <planeGeometry args={[4.25, 0.018]} />
            <meshBasicMaterial color="#70766d" transparent opacity={0.2} />
          </mesh>
        ))}
      </group>

      <group position={[0, 4.1, -0.25]}>
        <mesh castShadow>
          <cylinderGeometry args={[0.16, 0.95, 0.65, 16, 1, true]} />
          <meshStandardMaterial color="#24231d" roughness={0.75} metalness={0.35} side={THREE.DoubleSide} />
        </mesh>
        <mesh position={[0, -0.32, 0]}>
          <cylinderGeometry args={[0.5, 0.5, 0.04, 16]} />
          <meshBasicMaterial color="#e0a45e" />
        </mesh>
        <mesh position={[0, 1.1, 0]}>
          <cylinderGeometry args={[0.025, 0.025, 2, 8]} />
          <meshStandardMaterial color="#171611" />
        </mesh>
      </group>

      <FilingCabinet />

      <mesh position={[0, -2.35, 2.05]} rotation-x={-0.08} receiveShadow>
        <boxGeometry args={[11, 0.28, 4.1]} />
        <meshStandardMaterial map={deskTexture} roughness={0.82} />
      </mesh>
    </>
  );
}