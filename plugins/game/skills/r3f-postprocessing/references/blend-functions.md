# Reference — Blend Functions

Part of the `r3f-postprocessing` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## God Rays

```tsx
import { EffectComposer, GodRays } from '@react-three/postprocessing'
import { useRef } from 'react'

function Scene() {
  const sunRef = useRef<THREE.Mesh>(null!)

  return (
    <Canvas>
      {/* Sun mesh (light source for god rays) */}
      <mesh ref={sunRef} position={[0, 5, -10]}>
        <sphereGeometry args={[1]} />
        <meshBasicMaterial color="#ffddaa" />
      </mesh>

      <EffectComposer>
        {sunRef.current && (
          <GodRays
            sun={sunRef}
            blendFunction={BlendFunction.SCREEN}
            samples={60}
            density={0.96}
            decay={0.9}
            weight={0.4}
            exposure={0.6}
            clampMax={1}
            blur
          />
        )}
      </EffectComposer>
    </Canvas>
  )
}
```

## LUT (Color Lookup Table)

```tsx
import { EffectComposer, LUT } from '@react-three/postprocessing'
import { LUTCubeLoader } from 'postprocessing'
import { useLoader } from '@react-three/fiber'

function ColorGradedScene() {
  const texture = useLoader(LUTCubeLoader, '/luts/cinematic.cube')

  return (
    <EffectComposer>
      <LUT lut={texture} />
    </EffectComposer>
  )
}
```

## Blend Functions

```tsx
import { BlendFunction } from 'postprocessing'

// Available blend functions:
BlendFunction.SKIP           // Skip blending
BlendFunction.ADD            // Additive
BlendFunction.ALPHA          // Alpha
BlendFunction.AVERAGE        // Average
BlendFunction.COLOR          // Color
BlendFunction.COLOR_BURN     // Color Burn
BlendFunction.COLOR_DODGE    // Color Dodge
BlendFunction.DARKEN         // Darken
BlendFunction.DIFFERENCE     // Difference
BlendFunction.DIVIDE         // Divide
BlendFunction.DST            // Destination
BlendFunction.EXCLUSION      // Exclusion
BlendFunction.HARD_LIGHT     // Hard Light
BlendFunction.HARD_MIX       // Hard Mix
BlendFunction.HUE            // Hue
BlendFunction.INVERT         // Invert
BlendFunction.INVERT_RGB     // Invert RGB
BlendFunction.LIGHTEN        // Lighten
BlendFunction.LINEAR_BURN    // Linear Burn
BlendFunction.LINEAR_DODGE   // Linear Dodge
BlendFunction.LINEAR_LIGHT   // Linear Light
BlendFunction.LUMINOSITY     // Luminosity
BlendFunction.MULTIPLY       // Multiply
BlendFunction.NEGATION       // Negation
BlendFunction.NORMAL         // Normal
BlendFunction.OVERLAY        // Overlay
BlendFunction.PIN_LIGHT      // Pin Light
BlendFunction.REFLECT        // Reflect
BlendFunction.SATURATION     // Saturation
BlendFunction.SCREEN         // Screen
BlendFunction.SET            // Set
BlendFunction.SOFT_LIGHT     // Soft Light
BlendFunction.SRC            // Source
BlendFunction.SUBTRACT       // Subtract
BlendFunction.VIVID_LIGHT    // Vivid Light
```

## Performance Tips

1. **Limit effect count**: Each effect adds rendering overhead
2. **Use multisampling wisely**: Higher values = slower performance
3. **Disable when not needed**: Toggle `enabled` prop
4. **Lower resolution**: Some effects have resolution props
5. **Profile with DevTools**: Monitor GPU usage

```tsx
// excerpt — not a complete module; see the surrounding section for context
// Disable all effects
<EffectComposer enabled={performanceMode}>
  ...
</EffectComposer>

// Reduce effect quality on mobile
const isMobile = /iPhone|iPad|Android/i.test(navigator.userAgent)

<EffectComposer multisampling={isMobile ? 0 : 8}>
  <Bloom mipmapBlur={!isMobile} radius={isMobile ? 0.4 : 0.8} />
  {!isMobile && <SSAO samples={16} />}
</EffectComposer>
```

