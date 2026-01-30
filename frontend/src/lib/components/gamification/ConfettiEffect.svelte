<script lang="ts">
	import { onMount } from 'svelte';

	let visible = $state(true);

	const colors = ['#ef4444', '#3b82f6', '#22c55e', '#eab308', '#a855f7', '#f97316'];
	const particles = Array.from({ length: 25 }, (_, i) => ({
		id: i,
		color: colors[i % colors.length],
		left: Math.random() * 100,
		delay: Math.random() * 0.5,
		duration: 1.5 + Math.random() * 1,
		size: 6 + Math.random() * 6,
		rotation: Math.random() * 360
	}));

	onMount(() => {
		const timer = setTimeout(() => { visible = false; }, 2000);
		return () => clearTimeout(timer);
	});
</script>

{#if visible}
	<div class="fixed inset-0 pointer-events-none z-50 overflow-hidden">
		{#each particles as p (p.id)}
			<div
				class="absolute rounded-sm"
				style="
					left: {p.left}%;
					top: -10px;
					width: {p.size}px;
					height: {p.size}px;
					background: {p.color};
					animation: confetti-fall {p.duration}s ease-in {p.delay}s forwards;
					transform: rotate({p.rotation}deg);
				"
			></div>
		{/each}
	</div>
{/if}
