<script lang="ts">
	interface Props {
		text?: string;
	}

	let { text = 'LADEN' }: Props = $props();
</script>

<div class="flex flex-col items-center justify-center py-12 gap-4">
	<div class="flex gap-2">
		<span class="w-3 h-3 bg-nes-green dark:bg-crt-green animate-pixel-blink" style="animation-delay: 0s;"></span>
		<span class="w-3 h-3 bg-nes-green dark:bg-crt-green animate-pixel-blink" style="animation-delay: 0.3s;"></span>
		<span class="w-3 h-3 bg-nes-green dark:bg-crt-green animate-pixel-blink" style="animation-delay: 0.6s;"></span>
	</div>
	<p class="text-[10px] text-parchment-400 dark:text-crt-green" style="font-family: 'Press Start 2P', monospace;">
		{text}...
	</p>
</div>
