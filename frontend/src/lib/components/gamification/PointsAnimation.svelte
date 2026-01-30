<script lang="ts">
	interface Props {
		points: number;
		bonus?: number;
	}

	let { points, bonus = 0 }: Props = $props();
</script>

<div class="fixed inset-0 flex items-center justify-center pointer-events-none z-50">
	<div class="animate-bounce-in text-center">
		<div
			class="text-5xl font-black drop-shadow-lg"
			style="background: linear-gradient(135deg, #eab308, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;"
		>
			<span class="animate-shimmer">+{points}</span>
		</div>
		{#if bonus > 0}
			<div class="text-sm font-semibold text-accent-500 mt-1 animate-float-up" style="animation-delay: 0.3s; animation-duration: 1.2s;">
				inkl. {bonus} Bonus!
			</div>
		{/if}
	</div>
</div>
