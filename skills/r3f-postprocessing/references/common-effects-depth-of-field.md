# Reference — Common Effects: Depth of Field

Part of the `r3f-postprocessing` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Quick Start

```tsx
import { Canvas } from '@react-three/fiber'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'

function Scene() {
  return (
    <Canvas>
      <ambientLight />
      <mesh>
        <boxGeometry />
        <meshStandardMaterial color="hotpink" emissive="hotpink" emissiveIntensity={2} />
      </mesh>

      <EffectComposer>
        <Bloom luminanceThreshold={0.5} luminanceSmoothing={0.9} intensity={1.5} />
        <Vignette offset={0.5} darkness={0.5} />
      </EffectComposer>
    </Canvas>
  )
}
```

## Installation

```bash
npm install @react-three/postprocessing postprocessing
```

## EffectComposer

The container for all post-processing effects.

```tsx
import { EffectComposer } from '@react-three/postprocessing'

function Scene() {
  return (
    <Canvas>
      {/* Scene content */}
      <mesh>...</mesh>

      {/* Post-processing - must be inside Canvas, after scene content */}
      <EffectComposer
        enabled={true}           // Toggle all effects
        depthBuffer={true}       // Enable depth buffer
        stencilBuffer={false}    // Enable stencil buffer
        autoClear={true}         // Auto clear before render
        multisampling={8}        // MSAA samples (0 to disable)
      >
        {/* Effects go here */}
      </EffectComposer>
    </Canvas>
  )
}
```

## Common Effects

### Bloom (Glow)

```tsx
// excerpt — not a complete module; see the surrounding section for context
import { EffectComposer, Bloom } from '@react-three/postprocessing'
import { BlendFunction } from 'postprocessing'

<EffectComposer>
  <Bloom
    intensity={1.0}              // Bloom intensity
    luminanceThreshold={0.9}     // Brightness threshold
    luminanceSmoothing={0.025}   // Smoothness of threshold
    mipmapBlur={true}            // Enable mipmap blur
    radius={0.8}                 // Bloom radius
    levels={8}                   // Mipmap levels
    blendFunction={BlendFunction.ADD}
  />
</EffectComposer>

// For objects to glow, use emissive materials
<mesh>
  <boxGeometry />
  <meshStandardMaterial
    color="black"
    emissive="#ff00ff"
    emissiveIntensity={2}
    toneMapped={false}  // Important for values > 1
  />
</mesh>
```

### Selective Bloom

```tsx
import { EffectComposer, Bloom, Selection, Select } from '@react-three/postprocessing'

function Scene() {
  return (
    <Canvas>
      <Selection>
        <EffectComposer>
          <Bloom
            luminanceThreshold={0}
            intensity={2}
            mipmapBlur
          />
        </EffectComposer>

        {/* This mesh will bloom */}
        <Select enabled>
          <mesh>
            <sphereGeometry />
            <meshStandardMaterial emissive="red" emissiveIntensity={2} toneMapped={false} />
          </mesh>
        </Select>

        {/* This mesh will NOT bloom */}
        <mesh position={[2, 0, 0]}>
          <boxGeometry />
          <meshStandardMaterial color="blue" />
        </mesh>
      </Selection>
    </Canvas>
  )
}
```

### Depth of Field

```tsx
import { EffectComposer, DepthOfField } from '@react-three/postprocessing'

<EffectComposer>
  <DepthOfField
    focusDistance={0}     // Focus distance (0 = auto)
    focalLength={0.02}    // Camera focal length
    bokehScale={2}        // Bokeh size
    height={480}          // Resolution height
  />
</EffectComposer>

// With target object
import { useRef } from 'react'

function Scene() {
  const targetRef = useRef<THREE.Mesh>(null!)

  return (
    <>
      <mesh ref={targetRef} position={[0, 0, -5]}>
        <boxGeometry />
        <meshStandardMaterial color="red" />
      </mesh>

      <EffectComposer>
        <DepthOfField
          target={targetRef}
          focalLength={0.02}
          bokehScale={2}
        />
      </EffectComposer>
    </>
  )
}
```

### Vignette

```tsx
import { EffectComposer, Vignette } from '@react-three/postprocessing'

<EffectComposer>
  <Vignette
    offset={0.5}          // Vignette size
    darkness={0.5}        // Vignette intensity
    eskil={false}         // Use Eskil's vignette technique
  />
</EffectComposer>
```

### Noise

```tsx
import { EffectComposer, Noise } from '@react-three/postprocessing'
import { BlendFunction } from 'postprocessing'

<EffectComposer>
  <Noise
    premultiply            // Multiply noise with input
    blendFunction={BlendFunction.ADD}
    opacity={0.5}
  />
</EffectComposer>
```

### Chromatic Aberration

```tsx
import { EffectComposer, ChromaticAberration } from '@react-three/postprocessing'
import { BlendFunction } from 'postprocessing'

<EffectComposer>
  <ChromaticAberration
    offset={[0.002, 0.002]}    // Color offset
    radialModulation={true}    // Apply radially
    modulationOffset={0.5}
    blendFunction={BlendFunction.NORMAL}
  />
</EffectComposer>
```

