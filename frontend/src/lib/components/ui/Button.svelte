<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
		size?: 'sm' | 'md' | 'lg';
		disabled?: boolean;
		type?: 'button' | 'submit';
		onclick?: () => void;
		class?: string;
		children: Snippet;
	}

	let {
		variant = 'primary',
		size = 'md',
		disabled = false,
		type = 'button',
		onclick,
		class: className = '',
		children
	}: Props = $props();

	const variantClasses: Record<string, string> = {
		primary: 'bg-nes-green text-white dark:bg-crt-dark-green dark:text-crt-green dark:border-crt-green',
		secondary: 'bg-parchment-300 text-parchment-400 dark:bg-crt-panel dark:text-crt-green',
		danger: 'bg-nes-red text-white',
		ghost: 'bg-transparent text-parchment-400 dark:text-crt-green border-transparent!'
	};

	const sizeClasses: Record<string, string> = {
		sm: 'px-3 py-1.5 text-[8px]',
		md: 'px-4 py-2 text-[9px]',
		lg: 'px-6 py-3 text-[10px]'
	};
</script>

<button
	{type}
	{disabled}
	{onclick}
	class="pixel-btn inline-flex items-center justify-center gap-2 {variantClasses[variant]} {sizeClasses[size]} {className}"
>
	{@render children()}
</button>
