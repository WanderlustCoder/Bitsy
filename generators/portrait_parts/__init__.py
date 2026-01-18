"""
Portrait Parts - Components for detailed portrait generation.

Provides specialized rendering for:
- Hair clusters with bezier-based strands
- Detailed facial features (eyes, nose, lips)
- Accessories (glasses, jewelry)
- Clothing with fabric folds
"""

from .hair import (
    HairCluster,
    HairStyle,
    render_hair_clusters,
    render_cluster,
    generate_hair_clusters,
    generate_wavy_clusters,
    generate_straight_clusters,
    generate_curly_clusters,
    generate_bangs_clusters,
    generate_stray_strands,
)

from .face import (
    render_nose,
    render_lips,
    render_eye,
    render_eyebrow,
    EyeExpression,
    EyeParams,
)

from .accessories import (
    render_glasses,
    render_earring,
    GlassesParams,
    GlassesStyle,
    EarringStyle,
)

from .clothing import (
    render_neckline,
    render_collar,
    ClothingStyle,
    ClothingParams,
    FabricType,
    create_clothing_ramp,
)

__all__ = [
    # Hair
    'HairCluster',
    'HairStyle',
    'render_hair_clusters',
    'render_cluster',
    'generate_hair_clusters',
    'generate_wavy_clusters',
    'generate_straight_clusters',
    'generate_curly_clusters',
    'generate_bangs_clusters',
    'generate_stray_strands',
    # Face
    'render_nose',
    'render_lips',
    'render_eye',
    'render_eyebrow',
    'EyeExpression',
    'EyeParams',
    # Accessories
    'render_glasses',
    'render_earring',
    'GlassesParams',
    'GlassesStyle',
    'EarringStyle',
    # Clothing
    'render_neckline',
    'render_collar',
    'ClothingStyle',
    'ClothingParams',
    'FabricType',
    'create_clothing_ramp',
]
