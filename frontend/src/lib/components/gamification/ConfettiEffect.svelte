<script lang="ts">
	import { onMount } from 'svelte';

	let visible = $state(true);

	const nesColors = ['#e74040', '#4080e0', '#40b830', '#f0b028', '#a040c0', '#f08020'];
	const particles = Array.from({ length: 30 }, (_, i) => ({
		id: i,
		color: nesColors[i % nesColors.length],
		left: Math.random() * 100,
		delay: Math.random() * 0.5,
		duration: 1.5 + Math.random() * 1,
		size: 6 + Math.floor(Math.random() * 3) * 2
	}));

	onMount(() => {
		const timer = setTimeout(() => { visible = false; }, 2500);
		return () => clearTimeout(timer);
	});
</script>

{#if visible}
	<div class="fixed inset-0 pointer-events-none z-50 overflow-hidden">
		{#each particles as p (p.id)}
			<div
				class="absolute"
				style="
					left: {p.left}%;
					top: -10px;
					width: {p.size}px;
					height: {p.size}px;
					background: {p.color};
					animation: pixel-confetti-fall {p.duration}s steps(8) {p.delay}s forwards;
					image-rendering: pixelated;
				"
			></div>
		{/each}
	</div>
{/if}
