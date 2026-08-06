# Reference — Common Effects: Outline

Part of the `r3f-postprocessing` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

### SSAO (Screen Space Ambient Occlusion)

```tsx
import { EffectComposer, SSAO } from '@react-three/postprocessing'
import { BlendFunction } from 'postprocessing'

<EffectComposer>
  <SSAO
    blendFunction={BlendFunction.MULTIPLY}
    samples={30}              // Amount of samples
    radius={5}                // Occlusion radius
    intensity={30}            // Occlusion intensity
    luminanceInfluence={0.6}
    color="black"
    worldDistanceThreshold={100}
    worldDistanceFalloff={5}
    worldProximityThreshold={0.01}
    worldProximityFalloff={0.01}
  />
</EffectComposer>
```

### Outline

```tsx
import { EffectComposer, Outline, Selection, Select } from '@react-three/postprocessing'

function Scene() {
  return (
    <Canvas>
      <Selection>
        <EffectComposer autoClear={false}>
          <Outline
            visibleEdgeColor={0xffffff}    // Visible edge color
            hiddenEdgeColor={0x22090a}     // Hidden edge color
            edgeStrength={2.5}             // Edge strength
            pulseSpeed={0}                 // Pulse animation speed
            blur                           // Enable blur
            xRay                           // Show behind objects
          />
        </EffectComposer>

        {/* Outlined object */}
        <Select enabled>
          <mesh>
            <boxGeometry />
            <meshStandardMaterial color="orange" />
          </mesh>
        </Select>

        {/* Non-outlined object */}
        <mesh position={[2, 0, 0]}>
          <sphereGeometry />
          <meshStandardMaterial color="blue" />
        </mesh>
      </Selection>
    </Canvas>
  )
}
```

### Color Grading

```tsx
import { EffectComposer, BrightnessContrast, HueSaturation } from '@react-three/postprocessing'

<EffectComposer>
  <BrightnessContrast
    brightness={0}     // -1 to 1
    contrast={0}       // -1 to 1
  />
  <HueSaturation
    hue={0}           // Hue rotation in radians
    saturation={0}    // -1 to 1
  />
</EffectComposer>
```

### Tone Mapping

```tsx
import { EffectComposer, ToneMapping } from '@react-three/postprocessing'
import { ToneMappingMode } from 'postprocessing'

<EffectComposer>
  <ToneMapping
    mode={ToneMappingMode.ACES_FILMIC}
    // Modes: LINEAR, REINHARD, REINHARD2, OPTIMIZED_CINEON, CINEON, ACES_FILMIC, AGX, NEUTRAL
    resolution={256}
    whitePoint={4.0}
    middleGrey={0.6}
    minLuminance={0.01}
    averageLuminance={1.0}
    adaptationRate={1.0}
  />
</EffectComposer>
```

### Glitch

```tsx
import { EffectComposer, Glitch } from '@react-three/postprocessing'
import { GlitchMode } from 'postprocessing'

<EffectComposer>
  <Glitch
    delay={[1.5, 3.5]}           // Min/max delay between glitches
    duration={[0.6, 1.0]}        // Min/max duration
    strength={[0.3, 1.0]}        // Min/max strength
    mode={GlitchMode.SPORADIC}   // DISABLED, SPORADIC, CONSTANT_MILD, CONSTANT_WILD
    active                       // Enable/disable
    ratio={0.85}                 // Glitch ratio (0 = none, 1 = always)
  />
</EffectComposer>
```

### Pixelation

```tsx
import { EffectComposer, Pixelation } from '@react-three/postprocessing'

<EffectComposer>
  <Pixelation
    granularity={5}    // Pixel size
  />
</EffectComposer>
```

### Scanline

```tsx
import { EffectComposer, Scanline } from '@react-three/postprocessing'
import { BlendFunction } from 'postprocessing'

<EffectComposer>
  <Scanline
    blendFunction={BlendFunction.OVERLAY}
    density={1.25}     // Line density
    opacity={0.5}      // Effect opacity
  />
</EffectComposer>
```

### Grid

```tsx
import { EffectComposer, Grid } from '@react-three/postprocessing'
import { BlendFunction } from 'postprocessing'

<EffectComposer>
  <Grid
    blendFunction={BlendFunction.OVERLAY}
    scale={1.0}        // Grid scale
    lineWidth={0.0}    // Line width
  />
</EffectComposer>
```

### DotScreen

```tsx
import { EffectComposer, DotScreen } from '@react-three/postprocessing'
import { BlendFunction } from 'postprocessing'

<EffectComposer>
  <DotScreen
    blendFunction={BlendFunction.NORMAL}
    angle={Math.PI * 0.5}    // Pattern angle
    scale={1.0}              // Pattern scale
  />
</EffectComposer>
```

### SMAA (Anti-Aliasing)

```tsx
import { EffectComposer, SMAA } from '@react-three/postprocessing'

<EffectComposer multisampling={0}>  {/* Disable MSAA when using SMAA */}
  <SMAA />
</EffectComposer>
```

### FXAA (Anti-Aliasing)

```tsx
import { EffectComposer, FXAA } from '@react-three/postprocessing'

<EffectComposer multisampling={0}>
  <FXAA />
</EffectComposer>
```

