# Reference — Models: Suspense Patterns

Part of the `r3f-assets` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

### Suspense Patterns

#### Basic Suspense

```tsx
import { Suspense } from 'react'

function Scene() {
  return (
    <Canvas>
      <Suspense fallback={<Loader />}>
        <Model />
      </Suspense>
    </Canvas>
  )
}

function Loader() {
  return (
    <mesh>
      <boxGeometry />
      <meshBasicMaterial color="gray" wireframe />
    </mesh>
  )
}
```

#### Loading Progress UI

```tsx
import { useProgress, Html } from '@react-three/drei'

function Loader() {
  const { active, progress, errors, item, loaded, total } = useProgress()

  return (
    <Html center>
      <div className="loader">
        <div className="progress-bar">
          <div style={{ width: `${progress}%` }} />
        </div>
        <p>{Math.round(progress)}% loaded</p>
        <p>Loading: {item}</p>
      </div>
    </Html>
  )
}

function App() {
  return (
    <Canvas>
      <Suspense fallback={<Loader />}>
        <Scene />
      </Suspense>
    </Canvas>
  )
}
```

#### Drei Loader Component

```tsx
import { Loader } from '@react-three/drei'

function App() {
  return (
    <>
      <Canvas>
        <Suspense fallback={null}>
          <Scene />
        </Suspense>
      </Canvas>
      {/* HTML loading overlay */}
      <Loader />
    </>
  )
}
```

### Performance Tips

1. **Preload critical assets**: Avoid loading during interaction
2. **Use Draco compression**: Smaller file sizes
3. **Use LOD models**: Different detail levels for distance
4. **Clone instead of reload**: For multiple instances
5. **Lazy load non-critical**: Load on demand

```tsx
// Preload strategy
useGLTF.preload('/models/hero.glb')      // Critical
useTexture.preload('/textures/main.jpg')  // Critical

function LazyModel({ visible }) {
  // Only load when visible
  const { scene } = useGLTF(visible ? '/models/detail.glb' : null)
  return scene ? <primitive object={scene} /> : null
}
```

