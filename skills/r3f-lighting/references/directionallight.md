# Reference — directionalLight

Part of the `r3f-lighting` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Quick Start

```tsx
import { Canvas } from '@react-three/fiber'

function Scene() {
  return (
    <Canvas shadows>
      {/* Ambient fill */}
      <ambientLight intensity={0.5} />

      {/* Main light with shadows */}
      <directionalLight
        position={[5, 5, 5]}
        intensity={1}
        castShadow
        shadow-mapSize={[2048, 2048]}
      />

      {/* Objects */}
      <mesh castShadow receiveShadow>
        <boxGeometry />
        <meshStandardMaterial color="orange" />
      </mesh>

      {/* Ground */}
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#888" />
      </mesh>
    </Canvas>
  )
}
```

## Light Types Overview

| Light | Description | Shadow Support | Cost |
|-------|-------------|----------------|------|
| ambientLight | Uniform everywhere | No | Very Low |
| hemisphereLight | Sky/ground gradient | No | Very Low |
| directionalLight | Parallel rays (sun) | Yes | Low |
| pointLight | Omnidirectional (bulb) | Yes | Medium |
| spotLight | Cone-shaped | Yes | Medium |
| rectAreaLight | Area light (window) | No* | High |

## ambientLight

Illuminates all objects equally. No direction, no shadows.

```tsx
// excerpt — not a complete module; see the surrounding section for context
<ambientLight
  color="#ffffff"  // or color={new THREE.Color('#ffffff')}
  intensity={0.5}
/>
```

## hemisphereLight

Gradient from sky to ground. Good for outdoor scenes.

```tsx
// excerpt — not a complete module; see the surrounding section for context
<hemisphereLight
  color="#87ceeb"        // Sky color
  groundColor="#8b4513"  // Ground color
  intensity={0.6}
  position={[0, 50, 0]}
/>
```

## directionalLight

Parallel light rays. Simulates distant light (sun).

```tsx
// excerpt — not a complete module; see the surrounding section for context
<directionalLight
  color="#ffffff"
  intensity={1}
  position={[5, 10, 5]}

  // Shadow configuration
  castShadow
  shadow-mapSize={[2048, 2048]}
  shadow-camera-near={0.5}
  shadow-camera-far={50}
  shadow-camera-left={-10}
  shadow-camera-right={10}
  shadow-camera-top={10}
  shadow-camera-bottom={-10}
  shadow-bias={-0.0001}
  shadow-normalBias={0.02}
/>

// With target (light points at target)
function DirectionalWithTarget() {
  const lightRef = useRef<THREE.DirectionalLight>(null!)

  return (
    <>
      <directionalLight
        ref={lightRef}
        position={[5, 10, 5]}
        target-position={[0, 0, 0]}
      />
    </>
  )
}
```

## pointLight

Emits light in all directions. Like a light bulb.

```tsx
// excerpt — not a complete module; see the surrounding section for context
<pointLight
  color="#ffffff"
  intensity={1}
  position={[0, 5, 0]}
  distance={100}  // Maximum range (0 = infinite)
  decay={2}       // Light falloff (physically correct = 2)

  // Shadows
  castShadow
  shadow-mapSize={[1024, 1024]}
  shadow-camera-near={0.5}
  shadow-camera-far={50}
  shadow-bias={-0.005}
/>
```

## spotLight

Cone-shaped light. Like a flashlight.

```tsx
// excerpt — not a complete module; see the surrounding section for context
<spotLight
  color="#ffffff"
  intensity={1}
  position={[0, 10, 0]}
  angle={Math.PI / 6}     // Cone angle (max Math.PI/2)
  penumbra={0.5}          // Soft edge (0-1)
  distance={100}          // Range
  decay={2}               // Falloff

  // Target
  target-position={[0, 0, 0]}

  // Shadows
  castShadow
  shadow-mapSize={[1024, 1024]}
  shadow-camera-near={0.5}
  shadow-camera-far={50}
  shadow-camera-fov={30}
  shadow-bias={-0.0001}
/>

// SpotLight helper
import { useHelper } from '@react-three/drei'
import { SpotLightHelper } from 'three'

function SpotLightWithHelper() {
  const lightRef = useRef<THREE.SpotLight>(null!)
  useHelper(lightRef, SpotLightHelper, 'cyan')

  return <spotLight ref={lightRef} position={[0, 5, 0]} />
}
```

## rectAreaLight

Rectangular area light. Great for soft, realistic lighting.

```tsx
import { RectAreaLightHelper } from 'three/addons/helpers/RectAreaLightHelper.js'

function AreaLight() {
  const lightRef = useRef<THREE.RectAreaLight>(null!)

  return (
    <>
      <rectAreaLight
        ref={lightRef}
        color="#ffffff"
        intensity={5}
        width={4}
        height={2}
        position={[0, 5, 0]}
        rotation={[-Math.PI / 2, 0, 0]}  // Point downward
      />
    </>
  )
}

// Note: RectAreaLight only works with MeshStandardMaterial and MeshPhysicalMaterial
// Does not cast shadows natively
```

