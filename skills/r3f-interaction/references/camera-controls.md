# Reference — Camera Controls

Part of the `r3f-interaction` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Camera Controls

### OrbitControls

```tsx
import { OrbitControls } from '@react-three/drei'

function Scene() {
  return (
    <>
      <mesh>
        <boxGeometry />
        <meshStandardMaterial />
      </mesh>

      <OrbitControls
        makeDefault                    // Use as default controls
        enableDamping                  // Smooth movement
        dampingFactor={0.05}
        enableZoom={true}
        enablePan={true}
        enableRotate={true}
        autoRotate={false}
        autoRotateSpeed={2}
        minDistance={2}
        maxDistance={50}
        minPolarAngle={0}              // Top limit
        maxPolarAngle={Math.PI / 2}    // Horizon limit
        minAzimuthAngle={-Math.PI / 4} // Left limit
        maxAzimuthAngle={Math.PI / 4}  // Right limit
        target={[0, 1, 0]}             // Look-at point
      />
    </>
  )
}
```

### OrbitControls with Ref

```tsx
import { OrbitControls } from '@react-three/drei'
import { useRef, useEffect } from 'react'

function Scene() {
  const controlsRef = useRef<React.ComponentRef<typeof OrbitControls>>(null!)

  useEffect(() => {
    // Access controls methods
    if (controlsRef.current) {
      controlsRef.current.reset()
      controlsRef.current.target.set(0, 1, 0)
      controlsRef.current.update()
    }
  }, [])

  return <OrbitControls ref={controlsRef} />
}
```

### MapControls

Top-down map-style controls.

```tsx
import { MapControls } from '@react-three/drei'

<MapControls
  enableDamping
  dampingFactor={0.05}
  screenSpacePanning={false}  // Pan in world space
  maxPolarAngle={Math.PI / 2}
/>
```

### FlyControls

Free-flying camera controls.

```tsx
import { FlyControls } from '@react-three/drei'

<FlyControls
  movementSpeed={10}
  rollSpeed={Math.PI / 24}
  dragToLook
/>
```

### FirstPersonControls

FPS-style controls.

```tsx
import { FirstPersonControls } from '@react-three/drei'

<FirstPersonControls
  movementSpeed={10}
  lookSpeed={0.1}
  lookVertical
/>
```

### PointerLockControls

Lock pointer for FPS games.

```tsx
import { PointerLockControls } from '@react-three/drei'
import { useRef } from 'react'

function Scene() {
  const controlsRef = useRef<React.ComponentRef<typeof PointerLockControls>>(null!)

  return (
    <>
      <PointerLockControls ref={controlsRef} />

      {/* Click to lock pointer */}
      <mesh onClick={() => controlsRef.current?.lock()}>
        <planeGeometry args={[10, 10]} />
        <meshBasicMaterial color="green" />
      </mesh>
    </>
  )
}
```

### CameraControls

Advanced camera controls with smooth transitions.

```tsx
import { CameraControls } from '@react-three/drei'
import { useRef } from 'react'

function Scene() {
  const controlsRef = useRef<React.ComponentRef<typeof CameraControls>>(null!)

  const focusOnObject = async () => {
    // Smooth transition to target
    await controlsRef.current?.setLookAt(
      5, 3, 5,    // Camera position
      0, 0, 0,    // Look-at target
      true        // Enable transition
    )
  }

  return (
    <>
      <CameraControls ref={controlsRef} />

      <mesh onClick={focusOnObject}>
        <boxGeometry />
        <meshStandardMaterial color="red" />
      </mesh>
    </>
  )
}
```

### TrackballControls

Unconstrained rotation controls.

```tsx
import { TrackballControls } from '@react-three/drei'

<TrackballControls
  rotateSpeed={2.0}
  zoomSpeed={1.2}
  panSpeed={0.8}
  staticMoving={true}
/>
```

### ArcballControls

Arc-based rotation controls.

```tsx
import { ArcballControls } from '@react-three/drei'

<ArcballControls
  enableAnimations
  dampingFactor={25}
/>
```

