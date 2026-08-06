# Reference — Common Lighting Setups

Part of the `r3f-lighting` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Common Lighting Setups

### Three-Point Lighting

```tsx
function ThreePointLighting() {
  return (
    <>
      {/* Key light (main) */}
      <directionalLight
        position={[5, 5, 5]}
        intensity={1}
        castShadow
      />

      {/* Fill light (softer, opposite side) */}
      <directionalLight
        position={[-5, 3, 5]}
        intensity={0.5}
      />

      {/* Back light (rim lighting) */}
      <directionalLight
        position={[0, 5, -5]}
        intensity={0.3}
      />

      {/* Ambient fill */}
      <ambientLight intensity={0.2} />
    </>
  )
}
```

### Outdoor Daylight

```tsx
import { Sky, Environment } from '@react-three/drei'

function OutdoorLighting() {
  return (
    <>
      <Sky sunPosition={[100, 100, 100]} />
      <Environment preset="dawn" />

      <directionalLight
        position={[50, 100, 50]}
        intensity={1.5}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-far={200}
        shadow-camera-left={-50}
        shadow-camera-right={50}
        shadow-camera-top={50}
        shadow-camera-bottom={-50}
      />

      <hemisphereLight
        color="#87ceeb"
        groundColor="#8b4513"
        intensity={0.5}
      />
    </>
  )
}
```

### Studio Lighting

```tsx
import { Environment, Lightformer, ContactShadows } from '@react-three/drei'

function StudioLighting() {
  return (
    <>
      <Environment resolution={256}>
        {/* Key light */}
        <Lightformer
          form="rect"
          intensity={4}
          position={[5, 5, -5]}
          scale={[10, 5]}
          target={[0, 0, 0]}
        />

        {/* Fill light */}
        <Lightformer
          form="rect"
          intensity={2}
          position={[-5, 5, 5]}
          scale={[10, 5]}
        />

        {/* Rim light */}
        <Lightformer
          form="ring"
          intensity={1}
          position={[0, 5, -10]}
          scale={5}
        />
      </Environment>

      <ContactShadows
        position={[0, -0.5, 0]}
        opacity={0.5}
        blur={2}
      />
    </>
  )
}
```

## Animated Lighting

```tsx
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function AnimatedLight() {
  const lightRef = useRef<THREE.PointLight>(null!)

  useFrame(({ clock }) => {
    const t = clock.elapsedTime

    // Orbit around scene
    lightRef.current.position.x = Math.cos(t) * 5
    lightRef.current.position.z = Math.sin(t) * 5

    // Pulsing intensity
    lightRef.current.intensity = 1 + Math.sin(t * 2) * 0.5

    // Color cycling
    lightRef.current.color.setHSL((t * 0.1) % 1, 1, 0.5)
  })

  return (
    <pointLight ref={lightRef} position={[5, 3, 0]} castShadow />
  )
}
```

## Light Helpers

```tsx
import { useHelper } from '@react-three/drei'
import {
  DirectionalLightHelper,
  PointLightHelper,
  SpotLightHelper,
  HemisphereLightHelper,
} from 'three'

function LightWithHelpers() {
  const dirLightRef = useRef<THREE.DirectionalLight>(null!)
  const pointLightRef = useRef<THREE.PointLight>(null!)
  const spotLightRef = useRef<THREE.SpotLight>(null!)
  const hemiLightRef = useRef<THREE.HemisphereLight>(null!)

  useHelper(dirLightRef, DirectionalLightHelper, 5, 'red')
  useHelper(pointLightRef, PointLightHelper, 1, 'green')
  useHelper(spotLightRef, SpotLightHelper, 'blue')
  useHelper(hemiLightRef, HemisphereLightHelper, 5, 'yellow', 'brown')

  return (
    <>
      <directionalLight ref={dirLightRef} position={[5, 5, 5]} />
      <pointLight ref={pointLightRef} position={[-5, 5, 0]} />
      <spotLight ref={spotLightRef} position={[0, 5, 5]} />
      <hemisphereLight ref={hemiLightRef} />
    </>
  )
}
```

## Performance Tips

1. **Limit light count**: Each light adds shader complexity
2. **Use baked lighting**: For static scenes
3. **Smaller shadow maps**: 512-1024 often sufficient
4. **Tight shadow frustums**: Only cover needed area
5. **Disable unused shadows**: Not all lights need shadows
6. **Use Environment**: More efficient than many lights

```tsx
// excerpt — not a complete module; see the surrounding section for context
// Selective shadows
<mesh castShadow={isHero}>
  <boxGeometry />
</mesh>

// Only update shadows when needed
<ContactShadows frames={isAnimating ? Infinity : 1} />

// Use layers to exclude objects from lights
<directionalLight layers={1} />
<mesh layers={1}>  {/* Affected by light */}
<mesh layers={2}>  {/* Not affected */}
```

