<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		variant?: 'default' | 'points' | 'success' | 'danger' | 'warning';
		class?: string;
		children: Snippet;
	}

	let { variant = 'default', class: className = '', children }: Props = $props();

	const variantClasses: Record<string, string> = {
		default: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
		points: 'bg-accent-400/20 text-accent-500 dark:text-accent-400 font-semibold',
		success: 'bg-success-500/20 text-success-600 dark:text-success-500',
		danger: 'bg-danger-500/20 text-danger-600 dark:text-danger-500',
		warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
	};
</script>

<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs {variantClasses[variant]} {className}">
	{@render children()}
</span>
