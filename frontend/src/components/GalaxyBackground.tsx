import { useMemo } from 'react'

function Stars() {
  const layers = useMemo(() => {
    const counts = [60, 40, 25]
    const sizes = ['1px', '1.5px', '2px']
    const anims = ['animate-twinkle-slow', 'animate-twinkle-mid', 'animate-twinkle-fast']
    const ranges = [
      { x: [0, 100], y: [0, 100] },
      { x: [-10, 110], y: [-10, 110] },
      { x: [-20, 120], y: [-20, 120] },
    ]

    return counts.map((count, layer) =>
      Array.from({ length: count }, (_, i) => {
        const x = ranges[layer].x[0] + Math.random() * (ranges[layer].x[1] - ranges[layer].x[0])
        const y = ranges[layer].y[0] + Math.random() * (ranges[layer].y[1] - ranges[layer].y[0])
        const delay = Math.random() * 5
        return (
          <span
            key={`${layer}-${i}`}
            className={`fixed rounded-full bg-white ${anims[layer]}`}
            style={{
              left: `${x}%`,
              top: `${y}%`,
              width: sizes[layer],
              height: sizes[layer],
              animationDelay: `${delay}s`,
            }}
          />
        )
      })
    )
  }, [])

  return <>{layers}</>
}

function NebulaOrbs() {
  return (
    <>
      <div
        className="fixed left-1/4 top-1/3 -z-10 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 animate-pulse-glow rounded-full opacity-30 blur-[120px]"
        style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.2), transparent)' }}
      />
      <div
        className="fixed right-1/4 top-2/3 -z-10 h-[400px] w-[400px] animate-pulse-glow rounded-full opacity-25 blur-[100px]"
        style={{
          background: 'radial-gradient(circle, rgba(34,211,238,0.15), transparent)',
          animationDelay: '2s',
        }}
      />
      <div
        className="fixed left-1/2 top-1/4 -z-10 h-[350px] w-[350px] animate-pulse-glow rounded-full opacity-20 blur-[90px]"
        style={{
          background: 'radial-gradient(circle, rgba(167,139,250,0.15), transparent)',
          animationDelay: '4s',
        }}
      />
    </>
  )
}

function ShootingStars() {
  const stars = useMemo(
    () =>
      Array.from({ length: 3 }, (_, i) => (
        <span
          key={i}
          className="fixed h-[1.5px] w-[150px] animate-shoot opacity-0"
          style={{
            top: `${-20}%`,
            left: `${60 + i * 12}%`,
            rotate: '135deg',
            animationDelay: `${i * 4 + 2}s`,
            background: 'linear-gradient(to right, transparent, rgba(255,255,255,0.6))',
          }}
        />
      )),
    []
  )

  return <>{stars}</>
}

export function GalaxyBackground() {
  return (
    <div className="fixed inset-0 -z-20 overflow-hidden">
      <NebulaOrbs />
      <Stars />
      <ShootingStars />
    </div>
  )
}
