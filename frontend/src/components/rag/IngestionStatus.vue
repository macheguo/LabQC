<script setup>
import { computed } from 'vue'
import { Button } from '@/components/ui/button'
import { Database, Loader2, CheckCircle } from 'lucide-vue-next'

const props = defineProps({
  status: {
    type: Object,
    default: null,
  },
  ingesting: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['ingest'])

const statusLabel = computed(() => {
  if (!props.status) return 'unknown'
  return props.status.status || 'unknown'
})

const isReady = computed(() => statusLabel.value === 'ready')
const isNotIngested = computed(
  () => statusLabel.value === 'not_ingested' || statusLabel.value === 'unknown'
)
</script>

<template>
  <div class="ingestion-status">
    <div class="ingestion-status__content">
      <!-- Not ingested state -->
      <template v-if="isNotIngested && !ingesting">
        <Database :size="18" :stroke-width="1.75" class="ingestion-status__icon" />
        <div class="ingestion-status__info">
          <p class="ingestion-status__label">尚未摄入法规文档</p>
          <p class="ingestion-status__hint">
            请先摄入法规文档（PDF/Word），再开始智能问答。
          </p>
        </div>
        <Button size="sm" @click="emit('ingest')">摄入文档</Button>
      </template>

      <!-- Ingesting state -->
      <template v-else-if="ingesting">
        <Loader2
          :size="18"
          :stroke-width="1.75"
          class="ingestion-status__icon ingestion-status__icon--spin"
        />
        <div class="ingestion-status__info">
          <p class="ingestion-status__label">文档摄入中...</p>
          <p class="ingestion-status__hint">
            正在处理法规文档，请稍候。
          </p>
        </div>
      </template>

      <!-- Ready state -->
      <template v-else-if="isReady">
        <CheckCircle :size="18" :stroke-width="1.75" class="ingestion-status__icon ingestion-status__icon--ready" />
        <div class="ingestion-status__info">
          <p class="ingestion-status__label">文档库已就绪</p>
          <p class="ingestion-status__hint">
            <span v-if="status?.document_count">{{ status.document_count }} 份文档</span>
            <span v-if="status?.document_count && status?.chunk_count"> / </span>
            <span v-if="status?.chunk_count">{{ status.chunk_count }} 个片段已索引</span>
          </p>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.ingestion-status {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  padding: 16px 20px;
}

.ingestion-status__content {
  display: flex;
  align-items: center;
  gap: 14px;
}

.ingestion-status__icon {
  flex-shrink: 0;
  color: var(--text-muted);
}

.ingestion-status__icon--spin {
  animation: spin 0.8s linear infinite;
}

.ingestion-status__icon--ready {
  color: var(--color-success);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.ingestion-status__info {
  flex: 1;
  min-width: 0;
}

.ingestion-status__label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.ingestion-status__hint {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}
</style>
