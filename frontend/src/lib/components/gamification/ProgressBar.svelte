<script lang="ts">
	interface Props {
		value: number;
		class?: string;
	}

	let { value, class: className = '' }: Props = $props();

	let clamped = $derived(Math.max(0, Math.min(100, value)));
	let filledSegments = $derived(Math.floor(clamped / 10));
	let partialSegment = $derived(clamped % 10 > 0);
</script>

<div class="w-full {className}">
	<div class="flex gap-px h-4 border-3 border-[#5a3a1a] dark:border-crt-green bg-parchment-300 dark:bg-[#0a1a0a]">
		{#each Array(10) as _, i}
			<div
				class="flex-1 transition-colors duration-100 {i < filledSegments ? 'bg-nes-green dark:bg-crt-green' : i === filledSegments && partialSegment ? 'bg-nes-green/30 dark:bg-crt-green/30' : ''}"
			></div>
		{/each}
	</div>
	{#if clamped > 0}
		<div class="text-center mt-0.5">
			<span class="text-[8px] text-parchment-400 dark:text-crt-green" style="font-family: 'Press Start 2P', monospace;">
				{Math.round(clamped)}%
			</span>
		</div>
	{/if}
</div>
