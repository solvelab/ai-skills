# Reference — Procedural Walk Cycle (Bipedal Character)

Part of the `r3f-animation` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Performance Tips

1. **Isolate animated components**: Only the animated mesh re-renders
2. **Use refs over state**: Avoid React re-renders for animations
3. **Throttle expensive calculations**: Use delta accumulation
4. **Pause offscreen animations**: Check visibility
5. **Share animation clips**: Same clip for multiple instances

```tsx
// Isolate animation to prevent parent re-renders
function Scene() {
  return (
    <>
      <StaticMesh />   {/* Never re-renders */}
      <AnimatedMesh /> {/* Only this updates */}
    </>
  )
}

// Throttle expensive operations
function ThrottledAnimation() {
  const meshRef = useRef()
  const accumulated = useRef(0)

  useFrame((state, delta) => {
    accumulated.current += delta

    // Only update every 100ms
    if (accumulated.current > 0.1) {
      // Expensive calculation here
      accumulated.current = 0
    }

    // Cheap operations every frame
    meshRef.current.rotation.y += delta
  })
}
```

## Procedural Walk Cycle (Bipedal Character)

Complete procedural walk animation for low-poly humanoid characters using sine waves and biomechanical principles. No skeleton or GLTF required — works with primitive geometry groups.

### Biomechanical Reference Values

| Parameter | Value | Source |
|-----------|-------|--------|
| Walk cycle duration | 1.0–1.3s (2 steps) | Biomechanics standard |
| Steps per minute | 50–75 (natural walk) | mocaponline.com |
| Leg swing arc | 30–45° per direction | Animation reference |
| Arm swing arc | 25–35° (slightly less than legs) | Counter-motion principle |
| Body bob frequency | 2× leg frequency (bounce per step) | littlepolygon.com |
| Hip sway frequency | 0.5× leg frequency | littlepolygon.com |
| Torso counter-rotation | Opposes hip sway for balance | slynyrd.com |

### Key Principles

1. **Phase-locked to movement**: Walk phase advances with `delta`, not `clock.getElapsedTime()`. This prevents animation when stationary.
2. **Body bob**: Vertical bounce at 2× leg frequency — body rises at mid-step, falls at heel contact.
3. **Hip sway**: Lateral roll at half the leg frequency — left-right-left cadence.
4. **Torso counter-rotation**: Z-rotation opposes hip sway to maintain visual balance.
5. **Torso twist**: Y-rotation follows arm swing direction for natural spine movement.
6. **Arms oppose legs**: Right arm forward when left leg forward (counter-motion).
7. **Smooth blend**: Use `walkBlend` (0→1) to transition between idle and walk states smoothly — prevents animation snapping.
8. **Head bob**: Very subtle, follows body bob at reduced amplitude.

### Complete Implementation

```tsx
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// Walk cycle parameters (tuned for ~0.8 scale humanoid)
const WALK_FREQ = 5.5;           // ~1.14s per cycle = natural walk
const LEG_AMPLITUDE = 0.55;      // ~31° swing each direction
const ARM_AMPLITUDE = 0.45;      // ~26° swing, slightly less than legs
const BODY_BOB_HEIGHT = 0.03;    // vertical bounce amplitude
const BODY_BOB_FREQ = 2;         // 2x leg frequency (bounce per step)
const HIP_SWAY_AMPLITUDE = 0.025; // subtle lateral sway
const HIP_SWAY_FREQ = 0.5;      // half leg frequency
const TORSO_COUNTER_ROT = 0.08;  // torso Z opposes hip sway
const TORSO_TWIST = 0.06;        // torso Y-rotation with arm swing
const HEAD_BOB = 0.008;          // very subtle head vertical motion

// Idle parameters
const IDLE_SWAY_FREQ = 1.0;
const IDLE_SWAY_AMP = 0.012;
const IDLE_BREATHE_FREQ = 0.8;
const IDLE_BREATHE_AMP = 0.005;

function smoothDamp(current: number, target: number, speed: number): number {
  return current + (target - current) * speed;
}

export function WalkingCharacter() {
  const groupRef = useRef<THREE.Group>(null);
  const bodyRef = useRef<THREE.Group>(null);
  const torsoRef = useRef<THREE.Group>(null);
  const headRef = useRef<THREE.Mesh>(null);
  const leftLegRef = useRef<THREE.Group>(null);
  const rightLegRef = useRef<THREE.Group>(null);
  const leftArmRef = useRef<THREE.Group>(null);
  const rightArmRef = useRef<THREE.Group>(null);

  const prevPos = useRef(new THREE.Vector3());
  const targetRotation = useRef(0);
  const walkPhase = useRef(0);
  const walkBlend = useRef(0); // 0=idle, 1=walking

  useFrame(({ clock }, delta) => {
    if (!groupRef.current || !bodyRef.current) return;
    const t = clock.getElapsedTime();

    // --- Detect movement ---
    const currentPos = groupRef.current.position;
    const dx = currentPos.x - prevPos.current.x;
    const dz = currentPos.z - prevPos.current.z;
    const speed = Math.sqrt(dx * dx + dz * dz);
    const isWalking = speed > 0.001;
    prevPos.current.copy(currentPos);

    // Smooth walk blend (prevents snapping)
    walkBlend.current = smoothDamp(walkBlend.current, isWalking ? 1 : 0, 0.1);
    const wb = walkBlend.current;

    // Advance phase only when moving (phase-locked)
    if (isWalking) walkPhase.current += WALK_FREQ * delta;
    const phase = walkPhase.current;

    // --- Rotation toward movement direction ---
    if (isWalking) targetRotation.current = Math.atan2(dx, dz);
    let diff = targetRotation.current - bodyRef.current.rotation.y;
    while (diff > Math.PI) diff -= Math.PI * 2;
    while (diff < -Math.PI) diff += Math.PI * 2;
    bodyRef.current.rotation.y += diff * 0.15;

    // --- Body bob (2x frequency) ---
    bodyRef.current.position.y =
      Math.sin(phase * BODY_BOB_FREQ * Math.PI * 2) * BODY_BOB_HEIGHT * wb;

    // --- Hip sway (0.5x frequency) ---
    const hipSway =
      Math.sin(phase * HIP_SWAY_FREQ * Math.PI * 2) * HIP_SWAY_AMPLITUDE * wb;

    // --- Torso counter-rotation + twist ---
    if (torsoRef.current) {
      torsoRef.current.rotation.z =
        -hipSway * (TORSO_COUNTER_ROT / HIP_SWAY_AMPLITUDE) * wb;
      torsoRef.current.rotation.y =
        Math.sin(phase * Math.PI * 2) * TORSO_TWIST * wb;
    }

    // --- Legs (opposite phase) ---
    const legSwing = Math.sin(phase * Math.PI * 2) * LEG_AMPLITUDE * wb;
    if (leftLegRef.current) leftLegRef.current.rotation.x = legSwing;
    if (rightLegRef.current) rightLegRef.current.rotation.x = -legSwing;

    // --- Arms (opposite to legs) ---
    const armSwing = Math.sin(phase * Math.PI * 2) * ARM_AMPLITUDE * wb;
    if (leftArmRef.current) leftArmRef.current.rotation.x = -armSwing;
    if (rightArmRef.current) rightArmRef.current.rotation.x = armSwing;

    // --- Head bob ---
    if (headRef.current) {
      headRef.current.position.y =
        1.2 + Math.sin(phase * BODY_BOB_FREQ * Math.PI * 2) * HEAD_BOB * wb;
    }

    // --- Idle (breathing sway) ---
    if (wb < 0.1) {
      bodyRef.current.rotation.z = Math.sin(t * IDLE_SWAY_FREQ) * IDLE_SWAY_AMP;
      bodyRef.current.position.y = Math.sin(t * IDLE_BREATHE_FREQ) * IDLE_BREATHE_AMP;
    }
  });

  return (
    <group ref={groupRef}>
      <group ref={bodyRef} scale={0.8}>
        {/* Legs pivot at hip Y=0.45 */}
        <group ref={leftLegRef} position={[-0.1, 0.45, 0]}>
          {/* leg mesh + foot mesh */}
        </group>
        <group ref={rightLegRef} position={[0.1, 0.45, 0]}>
          {/* leg mesh + foot mesh */}
        </group>

        {/* Torso group (counter-rotation applied here) */}
        <group ref={torsoRef}>
          {/* torso mesh at Y=0.72 */}
          {/* shoulders at Y=0.9 */}

          {/* Arms pivot at shoulders */}
          <group ref={leftArmRef} position={[-0.22, 0.9, 0]}>
            {/* arm mesh + hand mesh */}
          </group>
          <group ref={rightArmRef} position={[0.22, 0.9, 0]}>
            {/* arm mesh + hand mesh */}
          </group>

          {/* Head with bob ref */}
          <mesh ref={headRef} position={[0, 1.2, 0]}>
            {/* head geometry */}
          </mesh>
        </group>
      </group>
    </group>
  );
}
```

### Hierarchy Structure (critical for correct animation)

```
group (position lerp)
  └── body (rotation Y = facing direction, position Y = body bob)
      ├── leftLeg (rotation X = walk swing)
      │   ├── leg cylinder
      │   └── foot box
      ├── rightLeg (rotation X = -walk swing)
      │   ├── leg cylinder
      │   └── foot box
      └── torso (rotation Z = counter-rot, rotation Y = twist)
          ├── torso cylinder
          ├── shoulders
          ├── leftArm (rotation X = -arm swing)
          │   ├── arm cylinder
          │   └── hand sphere
          ├── rightArm (rotation X = arm swing)
          │   ├── arm cylinder
          │   └── hand sphere
          ├── head (position Y = base + head bob)
          ├── eyes
          └── hair
```

### Tuning Tips

- **Too fast?** Reduce `WALK_FREQ` (5.5 → 4.0 for slow walk)
- **Too robotic?** Increase `BODY_BOB_HEIGHT` and `HIP_SWAY_AMPLITUDE`
- **Too exaggerated?** Reduce `LEG_AMPLITUDE` and `ARM_AMPLITUDE`
- **Snapping between idle/walk?** Reduce smoothDamp speed (0.1 → 0.05)
- **For running**: Increase `WALK_FREQ` to 8-10, `LEG_AMPLITUDE` to 0.7, `BODY_BOB_HEIGHT` to 0.06

## Procedural Jump Animation (Point-to-Point)

Smooth jump between two 3D positions with squash & stretch. No physics engine needed.

### Key Principles

1. **3 phases**: Prepare (squash down) → Fly (parabolic arc) → Land (squash on impact)
2. **Y arc**: `sin(t * PI) * height` — natural parabola, 0 at both ends, peak at midpoint
3. **XZ movement**: ease-in-out cubic — starts slow, fast in middle, slow at end
4. **Squash & stretch**: compress body before jump, elongate in air, compress on landing

### Reference Values

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Prepare duration | 0.15s | Anticipation squash |
| Fly duration | 0.6s | Arc through air |
| Land duration | 0.2s | Impact absorption |
| Jump height | 1.5-2.0 units | Peak of arc |
| Prepare squashY | 0.7 | Body compresses |
| Prepare stretchXZ | 1.15 | Body widens |
| Flight stretchY | 1.15 | Body elongates in air |
| Landing squashY | 0.75 | Impact compression |

### Implementation

```tsx
const JUMP_HEIGHT = 1.8;
const PREPARE_DURATION = 0.15;
const FLY_DURATION = 0.6;
const LAND_DURATION = 0.2;

type JumpPhase = 'idle' | 'prepare' | 'fly' | 'land';

function easeInOutCubic(t: number): number {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// In useFrame:
if (phase === 'prepare') {
  const t = Math.min(1, timer / PREPARE_DURATION);
  const squash = 1 - 0.3 * Math.sin(t * Math.PI / 2);
  const stretch = 1 + 0.15 * Math.sin(t * Math.PI / 2);
  body.scale.set(stretch, squash, stretch);
  // Stay at start position
}

if (phase === 'fly') {
  const t = Math.min(1, timer / FLY_DURATION);
  // XZ: ease-in-out
  const eased = easeInOutCubic(t);
  const x = startX + (endX - startX) * eased;
  const z = startZ + (endZ - startZ) * eased;
  // Y: sin arc
  const baseY = startY + (endY - startY) * eased;
  const arcY = Math.sin(t * Math.PI) * JUMP_HEIGHT;
  group.position.set(x, baseY + arcY, z);

  // Squash/stretch during flight
  if (t < 0.3) body.scale.set(0.9, 1.15, 0.9);      // rising: stretch
  else if (t < 0.7) body.scale.set(1, 1, 1);          // peak: normal
  else body.scale.set(0.92, 1.1, 0.92);               // falling: slight stretch
}

if (phase === 'land') {
  const t = Math.min(1, timer / LAND_DURATION);
  group.position.copy(endPos);
  if (t < 0.4) {
    // Impact squash
    body.scale.set(1.12, 0.75, 1.12);
  } else {
    // Recover to normal
    const r = (t - 0.4) / 0.6;
    body.scale.set(1.12 - 0.12 * r, 0.75 + 0.25 * r, 1.12 - 0.12 * r);
  }
}
```

### Tuning Tips

- **Floaty jump?** Reduce `FLY_DURATION` (0.6 → 0.4) or `JUMP_HEIGHT`
- **Too snappy?** Increase `PREPARE_DURATION` (0.15 → 0.25)
- **No weight?** Increase squash values (0.7 → 0.6) for more compression
- **Board game hop**: Use shorter `JUMP_HEIGHT` (1.0) and faster `FLY_DURATION` (0.4)
- **Long distance**: Increase `JUMP_HEIGHT` proportionally to XZ distance

