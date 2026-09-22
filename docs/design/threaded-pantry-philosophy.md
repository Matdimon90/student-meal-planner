# Threaded Pantry

*An algorithmic philosophy for the Student Meal Planner*

## The idea

A week of cooking is not a list of meals. It is a set of threads. An onion bought on Monday is still an onion on Wednesday; a bag of rice opened for lunch on day one is what makes dinner on day five possible. Threaded Pantry treats every ingredient as a strand that enters the week at the moment it is first opened, runs through the days it is used, and either ends cleanly — the package used up — or trails off as a loose end: the leftover. The picture that emerges is not an illustration of food. It is the shape of a plan that wastes nothing, drawn by the same logic that computes the plan.

## How it manifests in code

The system is seeded, so a given budget, seed or plan always draws the same braid. Each strand carries four numbers: the day it opens, the day it is last used, its weight (how much of the basket it represents) and its remainder (what is left when the week ends). Between day columns the strand is a cubic curve with horizontal tangents, so strands never cross at angles — they slide past each other the way things do on a shelf. Lane assignment is recomputed at every day from the set of strands currently alive, sorted by when they entered; when a strand ends, everything below it drifts upward to fill the space. That drift *is* the emergent behaviour: a week with heavy reuse relaxes into a few thick, calm bands, while a week of one-off ingredients becomes a nervous thicket of short strokes. The viewer reads efficiency without being told.

## Knots, tails and the pantry edge

Where a strand is actually cooked, the algorithm ties a knot: a small hollow node in the paper colour, so the eye can count uses along a thread. Where a strand ends with something left over, it does not stop — it falls a little, curling away from the day grid, and terminates in an amber bead whose radius is the remainder. Amber against deep green is the one contrast the piece allows itself; it is the only thing that should feel like an interruption, because a leftover is one. Strands that were already in the pantry before the week begins enter from the left edge as dashed lead-ins: they were not bought, and the drawing says so.

## Restraint as craftsmanship

The palette is the app's own — warm paper, deep green, a single amber — and the composition sits on the same dotted day-rules as the till receipt, so the art and the interface are one material. Stroke weights follow a gentle power curve rather than a linear map, tuned so the heaviest strand never bullies the picture and the lightest never disappears. Every constant in the implementation — the 0.42 tangent ratio, the 1.3 bias toward early opening, the 0.7 knot ratio — was chosen by looking at hundreds of seeds and keeping the values at which the braid reads as *inevitable* rather than random. This is the discipline of a meticulously crafted algorithm: the process is visible, but the tuning is invisible.

## Time

The drawing can be played. When it draws itself left to right, a vertical pen-line sweeps across the days and strands appear behind it, which is exactly what the planner does while it works: it decides one day at a time, carrying the pantry forward. The loading state is simply a frame of the algorithm caught mid-week. The finished plan is the same drawing, complete, with real ingredient names attached to the strands. Nothing is decorative; every mark is a fact about the week.
