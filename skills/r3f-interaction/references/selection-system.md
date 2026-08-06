# Reference — Selection System

Part of the `r3f-interaction` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Selection System

### Click to Select

```tsx
import { useState } from 'react'

function SelectableScene() {
  const [selected, setSelected] = useState(null)

  return (
    <>
      {[[-2, 0, 0], [0, 0, 0], [2, 0, 0]].map((position, i) => (
        <mesh
          key={i}
          position={position}
          onClick={(e) => {
            e.stopPropagation()
            setSelected(i)
          }}
        >
          <boxGeometry />
          <meshStandardMaterial
            color={selected === i ? 'hotpink' : 'orange'}
            emissive={selected === i ? 'hotpink' : 'black'}
            emissiveIntensity={0.3}
          />
        </mesh>
      ))}

      {/* Click on empty space to deselect */}
      <mesh
        position={[0, -1, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        onClick={() => setSelected(null)}
      >
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial color="gray" />
      </mesh>
    </>
  )
}
```

### Multi-Select with Outline

Selection highlighting via Outline/Selective Bloom is covered in r3f-postprocessing. The pointer-event selection state logic (tracking which ids are selected, shift-click to toggle) is the same pattern as Click to Select above, extended to a `Set`:

```tsx
const [selected, setSelected] = useState(new Set())

const toggleSelect = (id, event) => {
  event.stopPropagation()
  setSelected((prev) => {
    const next = new Set(prev)
    if (event.shiftKey) {
      next.has(id) ? next.delete(id) : next.add(id)
    } else {
      next.clear()
      next.add(id)
    }
    return next
  })
}
```

## Screen-Space to World-Space

### Get World Position from Click

```tsx
import { useThree } from '@react-three/fiber'
import * as THREE from 'three'

function ClickToPlace() {
  const { camera, raycaster, pointer } = useThree()
  const planeRef = useRef<THREE.Mesh>(null!)

  const handleClick = (event) => {
    // Create intersection plane
    const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0)
    const intersection = new THREE.Vector3()

    // Cast ray from pointer
    raycaster.setFromCamera(pointer, camera)
    raycaster.ray.intersectPlane(plane, intersection)

    console.log('World position:', intersection)
  }

  return (
    <mesh
      ref={planeRef}
      rotation={[-Math.PI / 2, 0, 0]}
      onClick={handleClick}
    >
      <planeGeometry args={[100, 100]} />
      <meshBasicMaterial visible={false} />
    </mesh>
  )
}
```

### World Position to Screen Position

```tsx
import { useThree, useFrame } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import * as THREE from 'three'

function WorldToScreen({ target }) {
  const { camera, size } = useThree()

  const getScreenPosition = (worldPos) => {
    const vector = worldPos.clone()
    vector.project(camera)

    return {
      x: (vector.x * 0.5 + 0.5) * size.width,
      y: (1 - (vector.y * 0.5 + 0.5)) * size.height
    }
  }

  // Or use Html component which handles this automatically
  return (
    <Html position={target}>
      <div className="label">Label</div>
    </Html>
  )
}
```

## Gesture Recognition

### usePinch and useWheel

```tsx
import { usePinch, useWheel } from '@use-gesture/react'
import { useSpring, animated } from '@react-spring/three'

function ZoomableMesh() {
  const [spring, api] = useSpring(() => ({
    scale: 1,
    config: { mass: 1, tension: 200, friction: 30 }
  }))

  usePinch(
    ({ offset: [s] }) => {
      api.start({ scale: s })
    },
    { target: window }
  )

  useWheel(
    ({ delta: [, dy] }) => {
      api.start({ scale: spring.scale.get() - dy * 0.001 })
    },
    { target: window }
  )

  return (
    <animated.mesh scale={spring.scale}>
      <boxGeometry />
      <meshStandardMaterial color="cyan" />
    </animated.mesh>
  )
}
```

## Scroll Controls

```tsx
import { Canvas } from '@react-three/fiber'
import { ScrollControls, Scroll, useScroll } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function AnimatedOnScroll() {
  const meshRef = useRef<THREE.Mesh>(null!)
  const scroll = useScroll()

  useFrame(() => {
    const offset = scroll.offset // 0 to 1
    meshRef.current.rotation.y = offset * Math.PI * 2
    meshRef.current.position.y = offset * 5
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}

export default function App() {
  return (
    <Canvas>
      <ScrollControls pages={3} damping={0.25}>
        <Scroll>
          <AnimatedOnScroll />
        </Scroll>

        {/* HTML content that scrolls */}
        <Scroll html>
          <h1 style={{ position: 'absolute', top: '10vh' }}>Page 1</h1>
          <h1 style={{ position: 'absolute', top: '110vh' }}>Page 2</h1>
          <h1 style={{ position: 'absolute', top: '210vh' }}>Page 3</h1>
        </Scroll>
      </ScrollControls>
    </Canvas>
  )
}
```

## Presentation Controls

For product showcases with limited rotation.

```tsx
import { PresentationControls } from '@react-three/drei'

function ProductShowcase() {
  return (
    <PresentationControls
      global                 // Apply to whole scene
      snap                   // Snap back when released
      speed={1}              // Rotation speed
      zoom={1}               // Zoom speed
      rotation={[0, 0, 0]}   // Initial rotation
      polar={[-Math.PI / 4, Math.PI / 4]}    // Vertical limits
      azimuth={[-Math.PI / 4, Math.PI / 4]}  // Horizontal limits
      config={{ mass: 1, tension: 170, friction: 26 }}
    >
      <mesh>
        <boxGeometry />
        <meshStandardMaterial color="gold" />
      </mesh>
    </PresentationControls>
  )
}
```

## Performance Tips

1. **Stop propagation**: Prevent unnecessary raycasts
2. **Use layers**: Filter raycast targets
3. **Simpler collision meshes**: Use invisible simple geometry
4. **Throttle events**: Limit onPointerMove frequency
5. **Disable controls when not needed**: `enabled={false}`

```tsx
// Use simpler geometry for raycasting
function OptimizedInteraction() {
  return (
    <group>
      {/* Complex visible mesh */}
      <mesh raycast={() => null}>
        <torusKnotGeometry args={[1, 0.4, 100, 16]} />
        <meshStandardMaterial color="purple" />
      </mesh>

      {/* Simple invisible collision mesh */}
      <mesh onClick={() => console.log('clicked')}>
        <sphereGeometry args={[1.5]} />
        <meshBasicMaterial visible={false} />
      </mesh>
    </group>
  )
}

// Throttle pointer move events
import { useMemo, useCallback } from 'react'
import throttle from 'lodash/throttle'

function ThrottledHover() {
  const handleMove = useMemo(
    () => throttle((e) => {
      console.log('Move', e.point)
    }, 100),
    []
  )

  return (
    <mesh onPointerMove={handleMove}>
      <boxGeometry />
      <meshStandardMaterial />
    </mesh>
  )
}
```

