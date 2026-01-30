<script lang="ts">
	interface Props {
		value: number;
		class?: string;
	}

	let { value, class: className = '' }: Props = $props();

	let clamped = $derived(Math.max(0, Math.min(100, value)));
</script>

<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 {className} relative overflow-hidden">
	<div
		class="h-3 rounded-full transition-all duration-500 relative"
		style="width: {clamped}%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #eab308);"
	>
		{#if clamped > 15}
			<span class="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-white drop-shadow-sm">
				{Math.round(clamped)}%
			</span>
		{/if}
	</div>
</div>
