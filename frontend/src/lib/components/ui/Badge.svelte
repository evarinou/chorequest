<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		variant?: 'default' | 'points' | 'success' | 'danger' | 'warning';
		class?: string;
		children: Snippet;
	}

	let { variant = 'default', class: className = '', children }: Props = $props();

	const variantClasses: Record<string, string> = {
		default: 'bg-parchment-200 text-parchment-400 border-parchment-300 dark:bg-crt-panel dark:text-crt-green dark:border-crt-border',
		points: 'bg-nes-gold/20 text-nes-gold border-nes-gold font-bold',
		success: 'bg-nes-green/20 text-nes-green border-nes-green',
		danger: 'bg-nes-red/20 text-nes-red border-nes-red',
		warning: 'bg-nes-orange/20 text-nes-orange border-nes-orange'
	};
</script>

<span
	class="inline-flex items-center px-2 py-0.5 text-xs border-2 font-[Press_Start_2P] text-[7px] leading-relaxed {variantClasses[variant]} {className}"
	style="font-family: 'Press Start 2P', monospace;"
>
	{@render children()}
</span>
