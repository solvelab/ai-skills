# Reference — Textures: Material Texture Maps Reference

Part of the `r3f-assets` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

### Render Targets

Render to texture.

```tsx
import { useFBO } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function RenderToTexture() {
  const fbo = useFBO(512, 512)
  const meshRef = useRef<THREE.Mesh>(null!)
  const otherSceneRef = useRef<THREE.Group>(null!)

  useFrame(({ gl, camera }) => {
    // Render other scene to FBO
    gl.setRenderTarget(fbo)
    gl.render(otherSceneRef.current, camera)
    gl.setRenderTarget(null)
  })

  return (
    <>
      {/* Scene to render to texture */}
      <group ref={otherSceneRef}>
        <mesh position={[0, 0, -5]}>
          <sphereGeometry args={[1, 32, 32]} />
          <meshStandardMaterial color="red" />
        </mesh>
      </group>

      {/* Display the texture */}
      <mesh ref={meshRef}>
        <planeGeometry args={[4, 4]} />
        <meshBasicMaterial map={fbo.texture} />
      </mesh>
    </>
  )
}
```

### Texture Atlas / Sprite Sheet

```tsx
import { useTexture } from '@react-three/drei'
import { useState } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

function SpriteAnimation() {
  const texture = useTexture('/textures/spritesheet.png')
  const [frame, setFrame] = useState(0)

  // Configure texture
  texture.wrapS = texture.wrapT = THREE.ClampToEdgeWrapping
  texture.repeat.set(1/4, 1/4)  // 4x4 sprite sheet

  useFrame(({ clock }) => {
    const newFrame = Math.floor(clock.elapsedTime * 10) % 16
    if (newFrame !== frame) {
      setFrame(newFrame)
      const col = newFrame % 4
      const row = Math.floor(newFrame / 4)
      texture.offset.set(col / 4, 1 - (row + 1) / 4)
    }
  })

  return (
    <mesh>
      <planeGeometry args={[1, 1]} />
      <meshBasicMaterial map={texture} transparent />
    </mesh>
  )
}
```

### Material Texture Maps Reference

```tsx
// excerpt — not a complete module; see the surrounding section for context
<meshStandardMaterial
  // Base color (sRGB)
  map={colorTexture}

  // Surface detail (Linear)
  normalMap={normalTexture}
  normalScale={[1, 1]}

  // Roughness (Linear, grayscale)
  roughnessMap={roughnessTexture}
  roughness={1}  // Multiplier

  // Metalness (Linear, grayscale)
  metalnessMap={metalnessTexture}
  metalness={1}  // Multiplier

  // Ambient Occlusion (Linear, requires uv2)
  aoMap={aoTexture}
  aoMapIntensity={1}

  // Self-illumination (sRGB)
  emissiveMap={emissiveTexture}
  emissive="#ffffff"
  emissiveIntensity={1}

  // Vertex displacement (Linear)
  displacementMap={displacementTexture}
  displacementScale={0.1}
  displacementBias={0}

  // Alpha (Linear)
  alphaMap={alphaTexture}
  transparent={true}

  // Environment reflection
  envMap={envTexture}
  envMapIntensity={1}

  // Lightmap (requires uv2)
  lightMap={lightmapTexture}
  lightMapIntensity={1}
/>
```

### Second UV Channel (for AO/Lightmaps)

```tsx
import { useEffect, useRef } from 'react'

function MeshWithUV2() {
  const meshRef = useRef<THREE.Mesh>(null!)

  useEffect(() => {
    // Copy uv to uv2 for aoMap/lightMap
    const geometry = meshRef.current.geometry
    geometry.setAttribute('uv2', geometry.attributes.uv)
  }, [])

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial
        aoMap={aoTexture}
        aoMapIntensity={1}
      />
    </mesh>
  )
}
```

### Suspense Loading

```tsx
import { Suspense } from 'react'
import { useTexture } from '@react-three/drei'

function TexturedMesh() {
  const texture = useTexture('/textures/large.jpg')
  return (
    <mesh>
      <boxGeometry />
      <meshStandardMaterial map={texture} />
    </mesh>
  )
}

function Fallback() {
  return (
    <mesh>
      <boxGeometry />
      <meshBasicMaterial color="gray" wireframe />
    </mesh>
  )
}

function Scene() {
  return (
    <Suspense fallback={<Fallback />}>
      <TexturedMesh />
    </Suspense>
  )
}
```

### Performance Tips

1. **Use power-of-2 dimensions**: 256, 512, 1024, 2048
2. **Compress textures**: Use KTX2/Basis for web
3. **Enable mipmaps**: For distant objects
4. **Limit texture size**: 2048 usually sufficient
5. **Reuse textures**: Same texture = better batching
6. **Preload important textures**: Avoid pop-in

```tsx
// Preload critical textures
useTexture.preload('/textures/hero.jpg')

// Check texture memory
useFrame(({ gl }) => {
  console.log('Textures:', gl.info.memory.textures)
})

// Dispose unused textures (R3F usually handles this)
texture.dispose()
```

