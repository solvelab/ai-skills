# Reference — shaderMaterial (Drei)

Part of the `r3f-shaders` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Quick Start

```tsx
import { Canvas, useFrame, extend } from '@react-three/fiber'
import { shaderMaterial } from '@react-three/drei'
import { useRef } from 'react'
import * as THREE from 'three'

// Create custom shader material
const ColorShiftMaterial = shaderMaterial(
  // Uniforms
  { time: 0, color: new THREE.Color(0.2, 0.0, 0.1) },
  // Vertex shader
  `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  // Fragment shader
  `
    uniform float time;
    uniform vec3 color;
    varying vec2 vUv;
    void main() {
      gl_FragColor = vec4(vUv.x + sin(time), vUv.y + cos(time), color.b, 1.0);
    }
  `
)

// Extend so it can be used as JSX
extend({ ColorShiftMaterial })

function ShaderMesh() {
  const materialRef = useRef<THREE.ShaderMaterial>(null!)

  useFrame(({ clock }) => {
    materialRef.current.time = clock.elapsedTime
  })

  return (
    <mesh>
      <planeGeometry args={[2, 2]} />
      {/* key={Material.key} enables HMR for shader development */}
      <colorShiftMaterial ref={materialRef} key={ColorShiftMaterial.key} />
    </mesh>
  )
}

export default function App() {
  return (
    <Canvas>
      <ShaderMesh />
    </Canvas>
  )
}
```

## shaderMaterial (Drei)

The recommended way to create shader materials in R3F.

### Basic Pattern

```tsx
import { shaderMaterial } from '@react-three/drei'
import { extend } from '@react-three/fiber'
import * as THREE from 'three'

// 1. Define the material
const MyShaderMaterial = shaderMaterial(
  // Uniforms object
  {
    time: 0,
    color: new THREE.Color(1, 0, 0),
    opacity: 1,
    map: null,
  },
  // Vertex shader (GLSL)
  `
    varying vec2 vUv;
    varying vec3 vPosition;

    void main() {
      vUv = uv;
      vPosition = position;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  // Fragment shader (GLSL)
  `
    uniform float time;
    uniform vec3 color;
    uniform float opacity;
    uniform sampler2D map;
    varying vec2 vUv;

    void main() {
      vec4 texColor = texture2D(map, vUv);
      gl_FragColor = vec4(color * texColor.rgb, opacity);
    }
  `
)

// 2. Extend R3F
extend({ MyShaderMaterial })

// 3. Use in component
function MyMesh() {
  const materialRef = useRef<THREE.ShaderMaterial>(null!)

  useFrame(({ clock }) => {
    materialRef.current.time = clock.elapsedTime
  })

  return (
    <mesh>
      <boxGeometry />
      {/* key prop enables Hot Module Replacement during development */}
      <myShaderMaterial
        ref={materialRef}
        key={MyShaderMaterial.key}
        color="hotpink"
        transparent
        opacity={0.8}
      />
    </mesh>
  )
}
```

### Hot Module Replacement (HMR)

The `key` prop on shaderMaterial enables live shader editing without page refresh:

```tsx
// excerpt — not a complete module; see the surrounding section for context
const MyMaterial = shaderMaterial(
  { time: 0 },
  vertexShader,
  fragmentShader
)

extend({ MyMaterial })

// MyMaterial.key changes when shader code changes
<myMaterial key={MyMaterial.key} />
```

When you edit shader code, the material automatically updates. Without `key`, you'd need to refresh the page to see changes.

### TypeScript Support

```tsx
import { shaderMaterial } from '@react-three/drei'
import { extend, ThreeElement } from '@react-three/fiber'
import * as THREE from 'three'

// Define uniform types
type WaveMaterialUniforms = {
  time: number
  amplitude: number
  color: THREE.Color
}

const WaveMaterial = shaderMaterial(
  {
    time: 0,
    amplitude: 0.5,
    color: new THREE.Color('hotpink'),
  } as WaveMaterialUniforms,
  // vertex shader
  `...`,
  // fragment shader
  `...`
)

// Extend with proper types
extend({ WaveMaterial })

// Declare for TypeScript (v9 pattern)
declare module '@react-three/fiber' {
  interface ThreeElements {
    waveMaterial: ThreeElement<typeof WaveMaterial>
  }
}
```

