import { Canvas, useLoader } from "@react-three/fiber";
import { PLYLoader } from "three/examples/jsm/loaders/PLYLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { extend } from "@react-three/fiber";
import * as THREE from "three";

extend({ OrbitControls });

export default function Preview({ url, onClose }) {
  return (
    <div className="overlay">
      <div className="viewer">
        <div className="viewerTop">
          <strong>Preview</strong>
          <button onClick={onClose}>Close</button>
        </div>
        <Canvas camera={{ position: [0, 0, 3], fov: 55 }}>
          <ambientLight intensity={1} />
          <Cloud url={url} />
          <OrbitControls args={[undefined, undefined]} />
        </Canvas>
      </div>
    </div>
  );
}

function Cloud({ url }) {
  const geometry = useLoader(PLYLoader, url);
  const hasColor = Boolean(geometry.getAttribute("color"));

  return (
    <points geometry={geometry}>
      <pointsMaterial
        size={0.01}
        vertexColors={hasColor}
        color={hasColor ? undefined : new THREE.Color("white")}
      />
    </points>
  );
}
