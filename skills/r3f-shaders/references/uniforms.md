# Reference — Uniforms

Part of the `r3f-shaders` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Raw THREE.ShaderMaterial

For full control without Drei helper.

```tsx
import { useFrame } from '@react-three/fiber'
import { useMemo, useRef } from 'react'
import * as THREE from 'three'

function CustomShaderMesh() {
  const materialRef = useRef()

  const shaderMaterial = useMemo(() => {
    return new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        color: { value: new THREE.Color('cyan') },
        resolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float time;
        uniform vec3 color;
        uniform vec2 resolution;
        varying vec2 vUv;

        void main() {
          vec2 st = gl_FragCoord.xy / resolution;
          float pattern = sin(st.x * 20.0 + time) * sin(st.y * 20.0 + time);
          gl_FragColor = vec4(color * pattern, 1.0);
        }
      `,
      side: THREE.DoubleSide,
      transparent: true,
    })
  }, [])

  useFrame(({ clock }) => {
    shaderMaterial.uniforms.time.value = clock.elapsedTime
  })

  return (
    <mesh material={shaderMaterial}>
      <planeGeometry args={[4, 4, 32, 32]} />
    </mesh>
  )
}
```

## Uniforms

### Common Uniform Types

```tsx
const MyMaterial = shaderMaterial(
  {
    // Numbers
    time: 0,
    intensity: 1.5,

    // Vectors
    resolution: new THREE.Vector2(1920, 1080),
    lightPosition: new THREE.Vector3(5, 10, 5),
    bounds: new THREE.Vector4(0, 0, 1, 1),

    // Color (becomes vec3)
    color: new THREE.Color('#ff0000'),

    // Matrices
    customMatrix: new THREE.Matrix4(),

    // Textures
    map: null,        // sampler2D
    cubeMap: null,    // samplerCube

    // Arrays
    positions: [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()],
  },
  vertexShader,
  fragmentShader
)
```

### GLSL Declarations

```glsl
// In shader code
uniform float time;
uniform float intensity;
uniform vec2 resolution;
uniform vec3 lightPosition;
uniform vec3 color;  // THREE.Color becomes vec3
uniform vec4 bounds;
uniform mat4 customMatrix;
uniform sampler2D map;
uniform samplerCube cubeMap;
uniform vec3 positions[3];
```

### Updating Uniforms

```tsx
function AnimatedShader() {
  const materialRef = useRef<THREE.ShaderMaterial>(null!)

  useFrame(({ clock, mouse, viewport }) => {
    // Direct value update
    materialRef.current.time = clock.elapsedTime

    // Vector update
    materialRef.current.resolution.set(viewport.width, viewport.height)

    // Color update
    materialRef.current.color.setHSL((clock.elapsedTime * 0.1) % 1, 1, 0.5)

    // Or via uniforms object (for THREE.ShaderMaterial)
    // materialRef.current.uniforms.time.value = clock.elapsedTime
  })

  return (
    <mesh>
      <boxGeometry />
      <myShaderMaterial ref={materialRef} />
    </mesh>
  )
}
```

## Varyings

Pass data from vertex to fragment shader.

```glsl
// Vertex shader
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vPosition;
varying vec3 vWorldPosition;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);
  vPosition = position;
  vWorldPosition = (modelMatrix * vec4(position, 1.0)).xyz;

  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}

// Fragment shader
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vPosition;
varying vec3 vWorldPosition;

void main() {
  // Use interpolated values
  gl_FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);
}
```

