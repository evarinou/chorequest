<script lang="ts">
	interface Props {
		points: number;
		bonus?: number;
	}

	let { points, bonus = 0 }: Props = $props();
</script>

<div class="fixed inset-0 flex items-center justify-center pointer-events-none z-50">
	<div class="text-center animate-pixel-damage">
		<div
			class="text-nes-gold dark:text-nes-gold drop-shadow-[2px_2px_0_#000]"
			style="font-family: 'Press Start 2P', monospace; font-size: 48px;"
		>
			+{points} XP
		</div>
		{#if bonus > 0}
			<div
				class="text-nes-orange dark:text-nes-orange mt-2 animate-pixel-float-up"
				style="font-family: 'Press Start 2P', monospace; font-size: 16px; animation-delay: 0.3s;"
			>
				BONUS +{bonus}!
			</div>
		{/if}
	</div>
</div>
