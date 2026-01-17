"""Tests for animation retargeting."""

import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rig import (
    BoneMapping,
    SkeletonMapping,
    RetargetingConfig,
    retarget_animation,
    retarget_pose,
    retarget_timeline,
    retarget_frame,
    create_mapping,
    list_mappings,
    infer_mapping,
    Pose,
    create_skeleton,
)
from animation.cycles import AnimationCycle, FrameData
from animation.timeline import Timeline, Track


class TestBoneMapping:
    """Tests for BoneMapping class."""

    def test_create_simple_mapping(self):
        """Test creating a simple one-to-one mapping."""
        mapping = BoneMapping(source='head', targets=['head'])
        assert mapping.source == 'head'
        assert mapping.targets == ['head']
        assert mapping.rotation_weights == [1.0]

    def test_create_split_mapping(self):
        """Test creating a one-to-many mapping."""
        mapping = BoneMapping(
            source='arm_l',
            targets=['arm_upper_l', 'arm_lower_l'],
            rotation_weights=[0.6, 0.4]
        )
        assert len(mapping.targets) == 2
        assert mapping.rotation_weights == [0.6, 0.4]

    def test_auto_weight_distribution(self):
        """Test automatic weight distribution."""
        mapping = BoneMapping(source='spine', targets=['spine_lower', 'spine_upper'])
        assert mapping.rotation_weights == [0.5, 0.5]

    def test_weight_normalization(self):
        """Test that weights are normalized to sum to 1.0."""
        mapping = BoneMapping(
            source='arm',
            targets=['a', 'b'],
            rotation_weights=[2.0, 2.0]
        )
        assert abs(sum(mapping.rotation_weights) - 1.0) < 0.001

    def test_position_scale(self):
        """Test position scale factor."""
        mapping = BoneMapping(source='leg', targets=['leg'], position_scale=1.5)
        assert mapping.position_scale == 1.5


class TestSkeletonMapping:
    """Tests for SkeletonMapping class."""

    def test_create_mapping(self):
        """Test creating a skeleton mapping."""
        mapping = SkeletonMapping(
            name='test',
            source_type='chibi',
            target_type='humanoid'
        )
        assert mapping.name == 'test'
        assert mapping.source_type == 'chibi'
        assert mapping.target_type == 'humanoid'

    def test_add_mapping(self):
        """Test adding bone mappings."""
        mapping = SkeletonMapping(
            name='test',
            source_type='a',
            target_type='b'
        )
        mapping.add_mapping('head', ['head'])
        mapping.add_mapping('arm_l', ['arm_upper_l', 'arm_lower_l'], [0.6, 0.4])

        assert mapping.has_mapping('head')
        assert mapping.has_mapping('arm_l')
        assert not mapping.has_mapping('leg')

    def test_get_mapping(self):
        """Test retrieving bone mappings."""
        mapping = SkeletonMapping(name='test', source_type='a', target_type='b')
        mapping.add_mapping('spine', ['spine_lower', 'spine_upper'])

        bone_mapping = mapping.get_mapping('spine')
        assert bone_mapping is not None
        assert bone_mapping.targets == ['spine_lower', 'spine_upper']

    def test_get_missing_mapping(self):
        """Test retrieving non-existent mapping."""
        mapping = SkeletonMapping(name='test', source_type='a', target_type='b')
        assert mapping.get_mapping('nonexistent') is None

    def test_root_scale(self):
        """Test root scale configuration."""
        mapping = SkeletonMapping(
            name='test',
            source_type='a',
            target_type='b',
            root_scale=(1.5, 2.0)
        )
        assert mapping.root_scale == (1.5, 2.0)


class TestRetargetingConfig:
    """Tests for RetargetingConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RetargetingConfig()
        assert config.scale_positions is True
        assert config.preserve_root_motion is True
        assert config.clamp_rotations is False
        assert config.rotation_limit == 2.0

    def test_custom_config(self):
        """Test custom configuration."""
        config = RetargetingConfig(
            scale_positions=False,
            clamp_rotations=True,
            rotation_limit=1.5
        )
        assert config.scale_positions is False
        assert config.clamp_rotations is True
        assert config.rotation_limit == 1.5


class TestRetargetPose:
    """Tests for pose retargeting."""

    def test_retarget_simple_pose(self):
        """Test retargeting a simple pose."""
        pose = Pose(
            name='test',
            rotations={'head': 0.5, 'spine': 0.3}
        )

        mapping = SkeletonMapping(name='test', source_type='a', target_type='b')
        mapping.add_mapping('head', ['head'])
        mapping.add_mapping('spine', ['spine_lower', 'spine_upper'], [0.5, 0.5])

        result = retarget_pose(pose, mapping)

        assert 'head' in result.rotations
        assert result.rotations['head'] == 0.5
        assert 'spine_lower' in result.rotations
        assert 'spine_upper' in result.rotations
        assert abs(result.rotations['spine_lower'] - 0.15) < 0.001
        assert abs(result.rotations['spine_upper'] - 0.15) < 0.001

    def test_retarget_pose_with_positions(self):
        """Test retargeting a pose with position data."""
        pose = Pose(
            name='test',
            positions={'root': (5.0, 10.0)}
        )

        mapping = SkeletonMapping(name='test', source_type='a', target_type='b')
        mapping.add_mapping('root', ['root'], position_scale=2.0)

        result = retarget_pose(pose, mapping)

        assert 'root' in result.positions
        assert result.positions['root'] == (10.0, 20.0)

    def test_retarget_unmapped_bones(self):
        """Test that unmapped bones are skipped."""
        pose = Pose(
            name='test',
            rotations={'head': 0.5, 'unmapped_bone': 1.0}
        )

        mapping = SkeletonMapping(name='test', source_type='a', target_type='b')
        mapping.add_mapping('head', ['head'])

        result = retarget_pose(pose, mapping)

        assert 'head' in result.rotations
        assert 'unmapped_bone' not in result.rotations

    def test_retarget_pose_preserves_metadata(self):
        """Test that pose metadata is preserved."""
        pose = Pose(
            name='crouch',
            rotations={'spine': 0.3},
            duration=0.5,
            easing='ease_out'
        )

        mapping = SkeletonMapping(name='test', source_type='a', target_type='b')
        mapping.add_mapping('spine', ['spine'])

        result = retarget_pose(pose, mapping)

        assert result.duration == 0.5
        assert result.easing == 'ease_out'
        assert 'retargeted' in result.name


class TestRetargetFrame:
    """Tests for frame retargeting."""

    def test_retarget_simple_frame(self):
        """Test retargeting a simple frame."""
        frame = FrameData(
            bone_rotations={'arm_l': 0.5},
            root_offset=(1.0, 2.0),
            duration=0.1
        )

        mapping = SkeletonMapping(
            name='test',
            source_type='a',
            target_type='b',
            root_scale=(2.0, 2.0)
        )
        mapping.add_mapping('arm_l', ['arm_upper_l', 'arm_lower_l'], [0.6, 0.4])

        result = retarget_frame(frame, mapping)

        assert 'arm_upper_l' in result.bone_rotations
        assert 'arm_lower_l' in result.bone_rotations
        assert abs(result.bone_rotations['arm_upper_l'] - 0.3) < 0.001
        assert abs(result.bone_rotations['arm_lower_l'] - 0.2) < 0.001
        assert result.root_offset == (2.0, 4.0)
        assert result.duration == 0.1

    def test_retarget_frame_with_offsets(self):
        """Test retargeting a frame with bone offsets."""
        frame = FrameData(
            bone_offsets={'leg_l': (0.5, 1.0)},
            duration=0.1
        )

        mapping = SkeletonMapping(name='test', source_type='a', target_type='b')
        mapping.add_mapping('leg_l', ['leg_upper_l', 'leg_lower_l'], position_scale=2.0)

        result = retarget_frame(frame, mapping)

        # Only first target gets the offset
        assert 'leg_upper_l' in result.bone_offsets
        assert result.bone_offsets['leg_upper_l'] == (1.0, 2.0)


class TestRetargetAnimation:
    """Tests for animation retargeting."""

    def test_retarget_animation(self):
        """Test retargeting a full animation."""
        animation = AnimationCycle(
            name='walk',
            frames=[
                FrameData(bone_rotations={'leg_l': 0.3, 'leg_r': -0.3}),
                FrameData(bone_rotations={'leg_l': -0.3, 'leg_r': 0.3}),
            ],
            loop=True,
            fps=12
        )

        mapping = create_mapping('chibi', 'humanoid')
        result = retarget_animation(animation, mapping)

        assert len(result.frames) == 2
        assert result.loop is True
        assert result.fps == 12
        assert 'humanoid' in result.name

        # Check bone mapping worked
        assert 'leg_upper_l' in result.frames[0].bone_rotations
        assert 'leg_lower_l' in result.frames[0].bone_rotations

    def test_retarget_empty_animation(self):
        """Test retargeting an empty animation."""
        animation = AnimationCycle(name='empty', frames=[])
        mapping = create_mapping('chibi', 'humanoid')

        result = retarget_animation(animation, mapping)

        assert len(result.frames) == 0

    def test_retarget_animation_with_config(self):
        """Test retargeting with custom config."""
        animation = AnimationCycle(
            name='test',
            frames=[
                FrameData(bone_rotations={'arm_l': 3.0})  # Large rotation
            ]
        )

        mapping = create_mapping('chibi', 'humanoid')
        config = RetargetingConfig(clamp_rotations=True, rotation_limit=1.0)

        result = retarget_animation(animation, mapping, config)

        # Check rotation was clamped
        for bone, rot in result.frames[0].bone_rotations.items():
            assert abs(rot) <= 1.0


class TestRetargetTimeline:
    """Tests for timeline retargeting."""

    def test_retarget_timeline(self):
        """Test retargeting a timeline."""
        timeline = Timeline('walk', fps=12)

        track = Track('leg_l_rotation')
        track.add_keyframe(0.0, 0.3, 'linear')
        track.add_keyframe(0.5, -0.3, 'linear')
        timeline.add_track(track)

        mapping = create_mapping('chibi', 'humanoid')
        result = retarget_timeline(timeline, mapping)

        assert 'leg_upper_l_rotation' in result.tracks
        assert 'leg_lower_l_rotation' in result.tracks

    def test_retarget_root_tracks(self):
        """Test retargeting root motion tracks."""
        timeline = Timeline('walk', fps=12)

        root_x = Track('root_offset_x')
        root_x.add_keyframe(0.0, 0.0, 'linear')
        root_x.add_keyframe(1.0, 10.0, 'linear')
        timeline.add_track(root_x)

        mapping = SkeletonMapping(
            name='test',
            source_type='a',
            target_type='b',
            root_scale=(2.0, 1.0)
        )

        result = retarget_timeline(timeline, mapping)

        assert 'root_offset_x' in result.tracks
        # Check scaling was applied
        last_kf = result.tracks['root_offset_x'].keyframes[-1]
        assert last_kf.value == 20.0


class TestCreateMapping:
    """Tests for create_mapping function."""

    def test_create_chibi_to_humanoid(self):
        """Test creating chibi to humanoid mapping."""
        mapping = create_mapping('chibi', 'humanoid')
        assert mapping.source_type == 'chibi'
        assert mapping.target_type == 'humanoid'
        assert mapping.has_mapping('arm_l')
        assert mapping.has_mapping('leg_l')

    def test_create_humanoid_to_chibi(self):
        """Test creating humanoid to chibi mapping."""
        mapping = create_mapping('humanoid', 'chibi')
        assert mapping.source_type == 'humanoid'
        assert mapping.target_type == 'chibi'

    def test_create_identity_mapping(self):
        """Test creating identity mapping (same type)."""
        mapping = create_mapping('chibi', 'chibi')
        assert mapping.source_type == 'chibi'
        assert mapping.target_type == 'chibi'
        # Identity mapping should have no bone mappings
        assert len(mapping.bone_mappings) == 0

    def test_create_invalid_mapping(self):
        """Test creating mapping for invalid types."""
        try:
            create_mapping('invalid', 'types')
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert 'No mapping' in str(e)


class TestListMappings:
    """Tests for list_mappings function."""

    def test_list_mappings(self):
        """Test listing available mappings."""
        mappings = list_mappings()
        assert len(mappings) >= 6
        assert ('chibi', 'humanoid') in mappings
        assert ('humanoid', 'chibi') in mappings
        assert ('chibi', 'simple') in mappings


class TestInferMapping:
    """Tests for infer_mapping function."""

    def test_infer_mapping_same_bones(self):
        """Test inferring mapping with identical bone names."""
        source = create_skeleton('chibi')
        target = create_skeleton('chibi')

        mapping = infer_mapping(source, target)

        # Should have direct mappings for all bones
        assert mapping.has_mapping('head')
        assert mapping.has_mapping('spine')


class TestRoundTrip:
    """Tests for round-trip retargeting."""

    def test_chibi_humanoid_chibi(self):
        """Test retargeting chibi -> humanoid -> chibi."""
        original = Pose(
            name='test',
            rotations={
                'head': 0.1,
                'spine': 0.2,
                'arm_l': 0.3,
                'arm_r': -0.3,
                'leg_l': 0.4,
                'leg_r': -0.4,
            }
        )

        # Chibi -> Humanoid
        to_humanoid = create_mapping('chibi', 'humanoid')
        humanoid_pose = retarget_pose(original, to_humanoid)

        # Humanoid -> Chibi
        to_chibi = create_mapping('humanoid', 'chibi')
        result = retarget_pose(humanoid_pose, to_chibi)

        # Rotations should be similar (not exact due to weight distribution)
        assert 'head' in result.rotations
        assert 'spine' in result.rotations
        assert 'arm_l' in result.rotations

        # Head should be exact (1:1 mapping)
        assert abs(result.rotations['head'] - original.rotations['head']) < 0.001


class TestIntegration:
    """Integration tests with real animation cycles."""

    def test_retarget_walk_cycle(self):
        """Test retargeting a walk cycle animation with correct bone names."""
        # Create a walk cycle with bone names matching our mapping
        walk_cycle = AnimationCycle(
            name='chibi_walk',
            frames=[
                FrameData(bone_rotations={'arm_l': 0.3, 'arm_r': -0.3, 'leg_l': 0.4, 'leg_r': -0.4}),
                FrameData(bone_rotations={'arm_l': 0.0, 'arm_r': 0.0, 'leg_l': 0.0, 'leg_r': 0.0}),
                FrameData(bone_rotations={'arm_l': -0.3, 'arm_r': 0.3, 'leg_l': -0.4, 'leg_r': 0.4}),
                FrameData(bone_rotations={'arm_l': 0.0, 'arm_r': 0.0, 'leg_l': 0.0, 'leg_r': 0.0}),
            ],
            loop=True,
            fps=12
        )

        mapping = create_mapping('chibi', 'humanoid')
        humanoid_walk = retarget_animation(walk_cycle, mapping)

        # Verify structure
        assert len(humanoid_walk.frames) == len(walk_cycle.frames)
        assert humanoid_walk.loop == walk_cycle.loop
        assert humanoid_walk.fps == walk_cycle.fps

        # Verify bone names transformed
        all_bones = set()
        for frame in humanoid_walk.frames:
            all_bones.update(frame.bone_rotations.keys())

        # Should have humanoid bone names (upper/lower limbs)
        assert any('upper' in b or 'lower' in b for b in all_bones)

    def test_retarget_preserves_timing(self):
        """Test that retargeting preserves animation timing."""
        animation = AnimationCycle(
            name='test',
            frames=[
                FrameData(bone_rotations={'head': 0.1}, duration=0.1),
                FrameData(bone_rotations={'head': 0.2}, duration=0.2),
                FrameData(bone_rotations={'head': 0.3}, duration=0.15),
            ]
        )

        mapping = create_mapping('chibi', 'humanoid')
        result = retarget_animation(animation, mapping)

        # Check durations preserved
        assert result.frames[0].duration == 0.1
        assert result.frames[1].duration == 0.2
        assert result.frames[2].duration == 0.15
