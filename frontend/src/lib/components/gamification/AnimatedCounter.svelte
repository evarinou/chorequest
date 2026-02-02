<script lang="ts">
	interface Props {
		value: number;
		duration?: number;
		class?: string;
	}

	let { value, duration = 800, class: className = '' }: Props = $props();

	let displayValue = $state(0);

	$effect(() => {
		const target = value;
		const start = displayValue;
		const diff = target - start;
		if (diff === 0) return;

		const startTime = performance.now();

		function easeOutCubic(t: number): number {
			return 1 - Math.pow(1 - t, 3);
		}

		function tick(now: number) {
			const elapsed = now - startTime;
			const progress = Math.min(elapsed / duration, 1);
			displayValue = Math.round(start + diff * easeOutCubic(progress));

			if (progress < 1) {
				requestAnimationFrame(tick);
			}
		}

		requestAnimationFrame(tick);
	});
</script>

<span class="tabular-nums {className}" style="font-family: 'VT323', monospace;">{displayValue}</span>
