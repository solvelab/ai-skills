# Reference — Instanced Shaders

Part of the `r3f-shaders` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Extending Built-in Materials

### onBeforeCompile

Modify existing material shaders.

```tsx
import { useRef, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

function ModifiedStandardMaterial() {
  const materialRef = useRef<THREE.MeshStandardMaterial>(null!)
  const shaderRef = useRef()

  useEffect(() => {
    if (materialRef.current) {
      materialRef.current.onBeforeCompile = (shader) => {
        // Add custom uniform
        shader.uniforms.time = { value: 0 }
        shaderRef.current = shader

        // Add uniform declaration
        shader.vertexShader = 'uniform float time;\n' + shader.vertexShader

        // Modify vertex shader
        shader.vertexShader = shader.vertexShader.replace(
          '#include <begin_vertex>',
          `
            #include <begin_vertex>
            transformed.y += sin(position.x * 10.0 + time) * 0.1;
          `
        )
      }
    }
  }, [])

  useFrame(({ clock }) => {
    if (shaderRef.current) {
      shaderRef.current.uniforms.time.value = clock.elapsedTime
    }
  })

  return (
    <mesh>
      <planeGeometry args={[5, 5, 32, 32]} />
      <meshStandardMaterial ref={materialRef} color="green" />
    </mesh>
  )
}
```

### Common Injection Points

```javascript
// Vertex shader chunks
'#include <begin_vertex>'       // After position is calculated
'#include <project_vertex>'     // After gl_Position
'#include <beginnormal_vertex>' // Normal calculation start

// Fragment shader chunks
'#include <color_fragment>'     // After diffuse color
'#include <output_fragment>'    // Final output
'#include <fog_fragment>'       // After fog applied
```

## GLSL Built-in Functions

### Math Functions

```glsl
// Basic
abs(x), sign(x), floor(x), ceil(x), fract(x)
mod(x, y), min(x, y), max(x, y), clamp(x, min, max)
mix(a, b, t), step(edge, x), smoothstep(edge0, edge1, x)

// Trigonometry
sin(x), cos(x), tan(x)
asin(x), acos(x), atan(y, x), atan(x)

// Exponential
pow(x, y), exp(x), log(x), sqrt(x)
```

### Vector Functions

```glsl
length(v), distance(p0, p1), dot(x, y), cross(x, y)
normalize(v), reflect(I, N), refract(I, N, eta)
```

## Instanced Shaders

```tsx
import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

function InstancedShaderMesh({ count = 1000 }) {
  const meshRef = useRef<THREE.InstancedMesh>(null!)

  // Create instance attributes
  const { offsets, colors } = useMemo(() => {
    const offsets = new Float32Array(count * 3)
    const colors = new Float32Array(count * 3)

    for (let i = 0; i < count; i++) {
      offsets[i * 3] = (Math.random() - 0.5) * 20
      offsets[i * 3 + 1] = (Math.random() - 0.5) * 20
      offsets[i * 3 + 2] = (Math.random() - 0.5) * 20

      colors[i * 3] = Math.random()
      colors[i * 3 + 1] = Math.random()
      colors[i * 3 + 2] = Math.random()
    }

    return { offsets, colors }
  }, [count])

  const shaderMaterial = useMemo(() => {
    return new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 }
      },
      vertexShader: `
        attribute vec3 offset;
        attribute vec3 instanceColor;
        varying vec3 vColor;

        void main() {
          vColor = instanceColor;
          vec3 pos = position + offset;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
        }
      `,
      fragmentShader: `
        varying vec3 vColor;

        void main() {
          gl_FragColor = vec4(vColor, 1.0);
        }
      `
    })
  }, [])

  useFrame(({ clock }) => {
    shaderMaterial.uniforms.time.value = clock.elapsedTime
  })

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]} material={shaderMaterial}>
      <boxGeometry args={[0.5, 0.5, 0.5]}>
        <instancedBufferAttribute attach="attributes-offset" args={[offsets, 3]} />
        <instancedBufferAttribute attach="attributes-instanceColor" args={[colors, 3]} />
      </boxGeometry>
    </instancedMesh>
  )
}
```

## External Shader Files

### With Vite/Webpack

```glsl
// shaders/vertex.glsl
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}

// shaders/fragment.glsl
uniform float time;
varying vec2 vUv;
void main() {
  gl_FragColor = vec4(vUv, sin(time), 1.0);
}

// Component.tsx
import vertexShader from './shaders/vertex.glsl?raw'
import fragmentShader from './shaders/fragment.glsl?raw'

const MyMaterial = shaderMaterial(
  { time: 0 },
  vertexShader,
  fragmentShader
)
```

### Vite Config for GLSL

```javascript
// vite.config.js
import glsl from 'vite-plugin-glsl'

export default {
  plugins: [glsl()]
}
```

## Material Properties

```tsx
// excerpt — not a complete module; see the surrounding section for context
<myShaderMaterial
  // Rendering
  transparent={true}
  opacity={1.0}
  side={THREE.DoubleSide}
  depthTest={true}
  depthWrite={true}

  // Blending
  blending={THREE.NormalBlending}
  // NormalBlending, AdditiveBlending, SubtractiveBlending, MultiplyBlending

  // Wireframe
  wireframe={false}

  // Custom uniforms
  time={0}
  color="hotpink"
/>
```

## Debugging Shaders

```tsx
function DebugShaderMesh() {
  const materialRef = useRef<THREE.ShaderMaterial>(null!)

  useEffect(() => {
    // Log compiled shaders
    if (materialRef.current) {
      console.log('Vertex:', materialRef.current.vertexShader)
      console.log('Fragment:', materialRef.current.fragmentShader)
    }
  }, [])

  return (
    <mesh>
      <boxGeometry />
      {/* Debug with visual output */}
      <shaderMaterial
        ref={materialRef}
        fragmentShader={`
          varying vec2 vUv;
          void main() {
            // Debug UV
            gl_FragColor = vec4(vUv, 0.0, 1.0);

            // Debug normals (in vertex: vNormal = normal)
            // gl_FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);
          }
        `}
        vertexShader={`
          varying vec2 vUv;
          void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `}
      />
    </mesh>
  )
}
```

## Performance Tips

1. **Minimize uniforms**: Group related values into vectors
2. **Avoid conditionals**: Use `mix`/`step` instead of `if/else`
3. **Precalculate in JS**: Move static calculations out of shaders
4. **Use textures for lookup**: Complex functions as texture lookups
5. **Limit overdraw**: Avoid unnecessary transparent objects

```glsl
// Instead of:
if (value > 0.5) {
  color = colorA;
} else {
  color = colorB;
}

// Use:
color = mix(colorB, colorA, step(0.5, value));
```

