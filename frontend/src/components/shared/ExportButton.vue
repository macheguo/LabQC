<script setup>
import { useI18n } from 'vue-i18n'
import { Download, Loader2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

const { t } = useI18n()

defineProps({
  label: {
    type: String,
    default: undefined,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['export'])
</script>

<template>
  <Button
    variant="outline"
    size="sm"
    :disabled="loading"
    @click="$emit('export')"
  >
    <Loader2 v-if="loading" :size="16" :stroke-width="1.75" class="animate-spin" />
    <Download v-else :size="16" :stroke-width="1.75" />
    <span>{{ loading ? t('shared.loading') : (label || t('qc.exportPdf')) }}</span>
  </Button>
</template>

<style scoped>
.animate-spin {
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
