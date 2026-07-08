import FeatureExplanation from './FeatureExplanation'

function resolveExplanation(explanations, legacyExplanation, key) {
  if (explanations?.[key]) return explanations[key]
  if (key === 'stress' && legacyExplanation?.feature_impacts) return legacyExplanation
  return null
}

export default function AssessmentExplanations({ explanations, explanation }) {
  const stress = resolveExplanation(explanations, explanation, 'stress')
  const fatigue = resolveExplanation(explanations, explanation, 'fatigue')
  const wellness = resolveExplanation(explanations, explanation, 'wellness')
  const hasAny = stress || fatigue || wellness

  return (
    <section className="space-y-4">
      <div className="text-center">
        <h3 className="text-xl font-semibold text-slate-900">Why these results?</h3>
        <p className="mt-1 text-sm text-slate-500">
          {hasAny
            ? 'Feature-level breakdown from your latest assessment'
            : 'Run an assessment to see stress, fatigue, and wellness explanations here'}
        </p>
      </div>

      <div className="mx-auto max-w-4xl space-y-6">
        <FeatureExplanation variant="stress" explanation={stress} />
        <FeatureExplanation variant="fatigue" explanation={fatigue} />
        <FeatureExplanation variant="wellness" explanation={wellness} />
      </div>
    </section>
  )
}
