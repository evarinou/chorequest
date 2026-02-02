<script lang="ts">
	import { onMount } from 'svelte';
	import type { LevelInfo } from '$lib/utils/level';

	interface Props {
		oldLevel: LevelInfo;
		newLevel: LevelInfo;
	}

	let { oldLevel, newLevel }: Props = $props();
	let visible = $state(true);

	onMount(() => {
		const timer = setTimeout(() => { visible = false; }, 3000);
		return () => clearTimeout(timer);
	});
</script>

{#if visible}
	<div class="fixed inset-0 z-[100] pointer-events-none flex items-center justify-center">
		<!-- Flash -->
		<div class="absolute inset-0" style="animation: level-up-flash 3s steps(4) forwards;"></div>

		<!-- Content -->
		<div class="text-center" style="animation: level-up-text 3s steps(6) forwards;">
			<div
				class="text-nes-gold drop-shadow-[3px_3px_0_#000] mb-4"
				style="font-family: 'Press Start 2P', monospace; font-size: 36px;"
			>
				LEVEL UP!
			</div>
			<div
				class="text-white dark:text-crt-green drop-shadow-[2px_2px_0_#000] mb-2"
				style="font-family: 'Press Start 2P', monospace; font-size: 18px;"
			>
				LV.{oldLevel.level} → LV.{newLevel.level}
			</div>
			<div
				class="text-nes-gold drop-shadow-[2px_2px_0_#000]"
				style="font-family: 'Press Start 2P', monospace; font-size: 12px;"
			>
				{newLevel.title}
			</div>
		</div>
	</div>
{/if}
