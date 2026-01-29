<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		open: boolean;
		title?: string;
		onclose: () => void;
		children: Snippet;
	}

	let { open, title = '', onclose, children }: Props = $props();

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') onclose();
	}

	function handleBackdrop() {
		onclose();
	}
</script>

{#if open}
	<!-- svelte-ignore a11y_no_noninteractive_element_interactions a11y_interactive_supports_focus -->
	<div
		class="fixed inset-0 z-50 flex items-center justify-center p-4"
		role="dialog"
		aria-modal="true"
		onkeydown={handleKeydown}
	>
		<div
			class="fixed inset-0 bg-black/50 transition-opacity"
			onclick={handleBackdrop}
			role="presentation"
		></div>
		<div class="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto z-10">
			{#if title}
				<div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
					<h2 class="text-lg font-semibold">{title}</h2>
					<button
						onclick={onclose}
						aria-label="Schließen"
						class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
					>
						<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
							<path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
						</svg>
					</button>
				</div>
			{/if}
			<div class="p-4">
				{@render children()}
			</div>
		</div>
	</div>
{/if}
