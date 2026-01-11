// TSS PPM v3.0 - Competency Types

export interface Competency {
  id: string
  level: string
  category: 'Dedicated' | 'Entrepreneurial' | 'Innovative'
  subcategory: string
  title_en: string
  title_nl?: string
  title_es?: string
  indicators_en?: string[]
  display_order: number
}

export interface CompetencyScore {
  competency_id: string
  score: number | null
  notes?: string
}

export type TovLevel = 'A' | 'B' | 'C' | 'D'
