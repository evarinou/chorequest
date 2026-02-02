<script lang="ts">
	interface Props {
		streak: number;
		size?: 'sm' | 'md' | 'lg';
	}

	let { streak, size = 'sm' }: Props = $props();

	let colorClass = $derived(
		streak >= 14 ? 'text-nes-red' :
		streak >= 7 ? 'text-nes-orange' :
		'text-nes-gold'
	);

	let textSize = $derived(
		size === 'lg' ? 'text-[12px]' :
		size === 'md' ? 'text-[9px]' :
		'text-[7px]'
	);

	let flameSize = $derived(
		size === 'lg' ? 'text-2xl' :
		size === 'md' ? 'text-lg' :
		'text-sm'
	);
</script>

{#if streak > 0}
	<div class="inline-flex items-center gap-1 {colorClass}" style="font-family: 'Press Start 2P', monospace;">
		<span class="animate-pixel-flame inline-block {flameSize}">🔥</span>
		<span class="{textSize}">{streak}</span>
	</div>
{/if}
