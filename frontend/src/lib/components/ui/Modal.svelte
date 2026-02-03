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
		class="fixed inset-0 z-50 flex items-center justify-center px-3 py-4 md:p-4"
		role="dialog"
		aria-modal="true"
		onkeydown={handleKeydown}
	>
		<div
			class="fixed inset-0 bg-black/80"
			onclick={handleBackdrop}
			role="presentation"
		></div>
		<div class="relative max-w-lg w-full max-h-[90vh] overflow-y-auto z-10 animate-pixel-pop-in">
			<!-- RPG Dialog Box -->
			<div class="pixel-border bg-parchment-50 dark:bg-crt-panel">
				{#if title}
					<div class="flex items-center justify-between px-4 py-2 bg-nes-blue dark:bg-crt-dark-green border-b-3 border-b-[#0005]">
						<h2 class="text-[10px] text-white dark:text-crt-green" style="font-family: 'Press Start 2P', monospace;">
							{title}
						</h2>
						<button
							onclick={onclose}
							aria-label="Schließen"
							class="text-white/70 hover:text-white dark:text-crt-green/70 dark:hover:text-crt-green text-[10px] min-w-[32px] min-h-[32px] flex items-center justify-center"
							style="font-family: 'Press Start 2P', monospace;"
						>
							X
						</button>
					</div>
				{/if}
				<div class="p-3 md:p-4">
					{@render children()}
				</div>
			</div>
		</div>
	</div>
{/if}
