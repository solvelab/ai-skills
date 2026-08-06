# Reference — Drei Lighting Helpers

Part of the `r3f-lighting` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Shadow Setup

### Enable Shadows on Canvas

```tsx
// excerpt — not a complete module; see the surrounding section for context
<Canvas
  shadows  // or shadows="soft" | "basic" | "percentage" | "variance"
>
```

### Shadow Types

```tsx
// excerpt — not a complete module; see the surrounding section for context
// Basic shadows (fastest, hard edges)
<Canvas shadows="basic">

// PCF shadows (default, filtered)
<Canvas shadows>

// Soft shadows (PCFSoft, softer edges)
<Canvas shadows="soft">

// VSM shadows (variance shadow map)
<Canvas shadows="variance">
```

### Configure Shadow-Casting Objects

```tsx
// excerpt — not a complete module; see the surrounding section for context
// Light must cast shadows
<directionalLight castShadow />

// Objects must cast and/or receive shadows
<mesh castShadow receiveShadow>
  <boxGeometry />
  <meshStandardMaterial />
</mesh>

// Ground typically only receives
<mesh receiveShadow>
  <planeGeometry args={[100, 100]} />
  <meshStandardMaterial />
</mesh>
```

### Shadow Camera Helper

```tsx
import { useHelper } from '@react-three/drei'
import { CameraHelper } from 'three'

function LightWithShadowHelper() {
  const lightRef = useRef<THREE.DirectionalLight>(null!)

  // Visualize shadow camera frustum
  useHelper(lightRef.current?.shadow.camera, CameraHelper)

  return (
    <directionalLight
      ref={lightRef}
      castShadow
      shadow-camera-left={-10}
      shadow-camera-right={10}
      shadow-camera-top={10}
      shadow-camera-bottom={-10}
    />
  )
}
```

## Drei Lighting Helpers

### Environment

HDR environment lighting with presets or custom files.

```tsx
// excerpt — not a complete module; see the surrounding section for context
import { Environment } from '@react-three/drei'

// Preset environments
<Environment
  preset="sunset"  // apartment, city, dawn, forest, lobby, night, park, studio, sunset, warehouse
  background       // Also use as background
  backgroundBlurriness={0}  // Background blur
  backgroundIntensity={1}   // Background brightness
  environmentIntensity={1}  // Lighting intensity
/>

// Custom HDR file
<Environment files="/hdri/studio.hdr" />

// Cube map (6 images)
<Environment
  files={['px.png', 'nx.png', 'py.png', 'ny.png', 'pz.png', 'nz.png']}
  path="/textures/cube/"
/>

// Ground projection
<Environment
  preset="city"
  ground={{
    height: 15,
    radius: 100,
    scale: 100,
  }}
/>
```

### Lightformer

Create custom light shapes inside Environment.

```tsx
import { Environment, Lightformer } from '@react-three/drei'

<Environment>
  <Lightformer
    form="ring"          // circle, ring, rect
    intensity={2}
    color="white"
    scale={10}
    position={[0, 5, -5]}
    target={[0, 0, 0]}   // Point at target
  />

  <Lightformer
    form="rect"
    intensity={1}
    color="red"
    scale={[5, 2]}
    position={[-5, 5, 0]}
  />
</Environment>
```

### Sky

Procedural sky with sun.

```tsx
import { Sky } from '@react-three/drei'

<Sky
  distance={450000}
  sunPosition={[0, 1, 0]}   // Or calculate from inclination/azimuth
  inclination={0.6}         // Sun elevation (0 = horizon, 0.5 = zenith)
  azimuth={0.25}            // Sun rotation around horizon
  turbidity={10}            // Haziness
  rayleigh={2}              // Light scattering
  mieCoefficient={0.005}
  mieDirectionalG={0.8}
/>
```

### Stars

Starfield background.

```tsx
import { Stars } from '@react-three/drei'

<Stars
  radius={100}      // Sphere radius
  depth={50}        // Depth of star distribution
  count={5000}      // Number of stars
  factor={4}        // Size factor
  saturation={0}    // Color saturation
  fade              // Fade at edges
  speed={1}         // Twinkle speed
/>
```

### Stage

Quick lighting setup for product showcase.

```tsx
import { Stage } from '@react-three/drei'

<Stage
  preset="rembrandt"  // rembrandt, portrait, upfront, soft
  intensity={1}
  shadows="contact"   // false, 'contact', 'accumulative', true
  environment="city"
  adjustCamera={1.2}  // Adjust camera to fit content
>
  <Model />
</Stage>
```

### ContactShadows

Fast fake shadows without shadow mapping.

```tsx
// excerpt — not a complete module; see the surrounding section for context
import { ContactShadows } from '@react-three/drei'

<ContactShadows
  position={[0, -0.5, 0]}
  opacity={0.5}
  scale={10}
  blur={1}
  far={10}
  resolution={256}
  color="#000000"
  frames={1}        // Render once (for static scenes)
/>

// For animated scenes
<ContactShadows frames={Infinity} />
```

### AccumulativeShadows

Soft, accumulated shadows.

```tsx
import { AccumulativeShadows, RandomizedLight } from '@react-three/drei'

<AccumulativeShadows
  position={[0, -0.5, 0]}
  scale={10}
  color="#316d39"
  opacity={0.8}
  frames={100}
  temporal          // Smooth accumulation over time
>
  <RandomizedLight
    amount={8}
    radius={4}
    ambient={0.5}
    intensity={1}
    position={[5, 5, -10]}
    bias={0.001}
  />
</AccumulativeShadows>
```

### SoftShadows

Enable PCF soft shadows globally.

```tsx
import { SoftShadows } from '@react-three/drei'

<Canvas shadows>
  <SoftShadows
    size={25}
    samples={10}
    focus={0}
  />
</Canvas>
```

### BakeShadows

Bake shadows for static scenes.

```tsx
import { BakeShadows } from '@react-three/drei'

<Canvas shadows>
  <BakeShadows />  {/* Bakes shadows once on mount */}
</Canvas>
```

