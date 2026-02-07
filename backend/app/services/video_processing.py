"""
Video Processing Service
Handles video upload, transcoding with AWS MediaConvert, and HLS streaming
"""

import boto3
import os
import asyncio
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.models.course import Lesson
from app.models.video_and_analytics import VideoAnalytics, VideoStatus


class VideoProcessingService:
    """Service for video processing and streaming"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        self.mediaconvert_client = boto3.client(
            'mediaconvert',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        self.bucket_name = os.getenv('AWS_S3_BUCKET', 'skillstudio-videos')
        self.cloudfront_domain = os.getenv('CLOUDFRONT_DOMAIN', '')
    
    async def initiate_video_upload(
        self, 
        db: AsyncSession, 
        lesson_id: UUID,
        filename: str
    ) -> Dict[str, str]:
        """
        Generate presigned URL for direct S3 upload
        Returns presigned URL and key
        """
        # Generate unique S3 key
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        s3_key = f"videos/raw/{lesson_id}/{timestamp}_{filename}"
        
        # Generate presigned POST URL
        presigned_post = self.s3_client.generate_presigned_post(
            Bucket=self.bucket_name,
            Key=s3_key,
            Fields={"acl": "private"},
            Conditions=[
                {"acl": "private"},
                ["content-length-range", 1, 524288000]  # 500MB max
            ],
            ExpiresIn=3600  # 1 hour
        )
        
        # Update lesson with upload status
        await db.execute(
            update(Lesson)
            .where(Lesson.id == lesson_id)
            .values(
                video_status='uploading',
                video_original_url=f"s3://{self.bucket_name}/{s3_key}"
            )
        )
        await db.commit()
        
        return {
            "upload_url": presigned_post['url'],
            "fields": presigned_post['fields'],
            "s3_key": s3_key
        }
    
    async def start_transcoding(
        self,
        db: AsyncSession,
        lesson_id: UUID,
        s3_key: str
    ) -> str:
        """
        Start AWS MediaConvert transcoding job
        Returns job ID
        """
        # Get MediaConvert endpoint
        endpoints = self.mediaconvert_client.describe_endpoints()
        mediaconvert_endpoint = endpoints['Endpoints'][0]['Url']
        
        # Create MediaConvert client with endpoint
        mc_client = boto3.client(
            'mediaconvert',
            endpoint_url=mediaconvert_endpoint,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        # Output paths
        output_path = f"s3://{self.bucket_name}/videos/transcoded/{lesson_id}/"
        
        # MediaConvert job settings
        job_settings = {
            "Role": os.getenv('MEDIACONVERT_ROLE_ARN'),
            "Settings": {
                "Inputs": [
                    {
                        "FileInput": f"s3://{self.bucket_name}/{s3_key}",
                        "AudioSelectors": {
                            "Audio Selector 1": {
                                "DefaultSelection": "DEFAULT"
                            }
                        },
                        "VideoSelector": {}
                    }
                ],
                "OutputGroups": [
                    {
                        "Name": "HLS",
                        "OutputGroupSettings": {
                            "Type": "HLS_GROUP_SETTINGS",
                            "HlsGroupSettings": {
                                "Destination": output_path,
                                "SegmentLength": 10,
                                "MinSegmentLength": 0,
                                "DirectoryStructure": "SINGLE_DIRECTORY",
                                "ManifestDurationFormat": "INTEGER",
                                "StreamInfResolution": "INCLUDE"
                            }
                        },
                        "Outputs": [
                            # 1080p
                            {
                                "NameModifier": "_1080p",
                                "VideoDescription": {
                                    "Width": 1920,
                                    "Height": 1080,
                                    "CodecSettings": {
                                        "Codec": "H_264",
                                        "H264Settings": {
                                            "Bitrate": 5000000,
                                            "RateControlMode": "CBR"
                                        }
                                    }
                                },
                                "AudioDescriptions": [
                                    {
                                        "CodecSettings": {
                                            "Codec": "AAC",
                                            "AacSettings": {
                                                "Bitrate": 128000,
                                                "CodingMode": "CODING_MODE_2_0",
                                                "SampleRate": 48000
                                            }
                                        }
                                    }
                                ],
                                "ContainerSettings": {
                                    "Container": "M3U8"
                                }
                            },
                            # 720p
                            {
                                "NameModifier": "_720p",
                                "VideoDescription": {
                                    "Width": 1280,
                                    "Height": 720,
                                    "CodecSettings": {
                                        "Codec": "H_264",
                                        "H264Settings": {
                                            "Bitrate": 3000000,
                                            "RateControlMode": "CBR"
                                        }
                                    }
                                },
                                "AudioDescriptions": [
                                    {
                                        "CodecSettings": {
                                            "Codec": "AAC",
                                            "AacSettings": {
                                                "Bitrate": 128000,
                                                "CodingMode": "CODING_MODE_2_0",
                                                "SampleRate": 48000
                                            }
                                        }
                                    }
                                ],
                                "ContainerSettings": {
                                    "Container": "M3U8"
                                }
                            },
                            # 480p
                            {
                                "NameModifier": "_480p",
                                "VideoDescription": {
                                    "Width": 854,
                                    "Height": 480,
                                    "CodecSettings": {
                                        "Codec": "H_264",
                                        "H264Settings": {
                                            "Bitrate": 1500000,
                                            "RateControlMode": "CBR"
                                        }
                                    }
                                },
                                "AudioDescriptions": [
                                    {
                                        "CodecSettings": {
                                            "Codec": "AAC",
                                            "AacSettings": {
                                                "Bitrate": 96000,
                                                "CodingMode": "CODING_MODE_2_0",
                                                "SampleRate": 48000
                                            }
                                        }
                                    }
                                ],
                                "ContainerSettings": {
                                    "Container": "M3U8"
                                }
                            }
                        ]
                    },
                    # Thumbnail output
                    {
                        "Name": "Thumbnails",
                        "OutputGroupSettings": {
                            "Type": "FILE_GROUP_SETTINGS",
                            "FileGroupSettings": {
                                "Destination": f"s3://{self.bucket_name}/videos/thumbnails/{lesson_id}/"
                            }
                        },
                        "Outputs": [
                            {
                                "ContainerSettings": {
                                    "Container": "RAW"
                                },
                                "VideoDescription": {
                                    "Width": 1280,
                                    "Height": 720,
                                    "CodecSettings": {
                                        "Codec": "FRAME_CAPTURE",
                                        "FrameCaptureSettings": {
                                            "FramerateNumerator": 1,
                                            "FramerateDenominator": 10,
                                            "MaxCaptures": 1,
                                            "Quality": 80
                                        }
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        # Create the job
        response = mc_client.create_job(**job_settings)
        job_id = response['Job']['Id']
        
        # Update lesson with job ID and status
        await db.execute(
            update(Lesson)
            .where(Lesson.id == lesson_id)
            .values(
                video_status='processing',
                transcoding_job_id=job_id,
                transcoding_progress=0
            )
        )
        await db.commit()
        
        return job_id
    
    async def check_transcoding_status(
        self,
        db: AsyncSession,
        lesson_id: UUID,
        job_id: str
    ) -> Dict[str, Any]:
        """Check status of MediaConvert job"""
        try:
            # Get MediaConvert endpoint
            endpoints = self.mediaconvert_client.describe_endpoints()
            mediaconvert_endpoint = endpoints['Endpoints'][0]['Url']
            
            mc_client = boto3.client(
                'mediaconvert',
                endpoint_url=mediaconvert_endpoint,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            response = mc_client.get_job(Id=job_id)
            job = response['Job']
            
            status = job['Status']
            progress = job.get('JobPercentComplete', 0)
            
            # Update lesson progress
            await db.execute(
                update(Lesson)
                .where(Lesson.id == lesson_id)
                .values(transcoding_progress=progress)
            )
            
            # If complete, update with HLS URL
            if status == 'COMPLETE':
                hls_url = f"https://{self.cloudfront_domain}/videos/transcoded/{lesson_id}/index.m3u8"
                thumbnail_url = f"https://{self.cloudfront_domain}/videos/thumbnails/{lesson_id}/index.00001.jpg"
                
                # Get video duration from job output
                duration_seconds = job.get('Timing', {}).get('DurationInMs', 0) // 1000
                
                await db.execute(
                    update(Lesson)
                    .where(Lesson.id == lesson_id)
                    .values(
                        video_status='ready',
                        video_hls_url=hls_url,
                        video_thumbnail_url=thumbnail_url,
                        video_duration_seconds=duration_seconds,
                        video_quality_variants=['1080p', '720p', '480p'],
                        transcoding_progress=100
                    )
                )
            elif status == 'ERROR':
                await db.execute(
                    update(Lesson)
                    .where(Lesson.id == lesson_id)
                    .values(video_status='failed')
                )
            
            await db.commit()
            
            return {
                "status": status.lower(),
                "progress": progress,
                "job_id": job_id
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def track_video_watch(
        self,
        db: AsyncSession,
        lesson_id: UUID,
        user_id: UUID,
        watch_duration_seconds: int,
        completion_percentage: float,
        playback_speed: float = 1.0,
        quality_selected: Optional[str] = None,
        device_type: Optional[str] = None
    ):
        """Record video watch analytics"""
        analytics = VideoAnalytics(
            lesson_id=lesson_id,
            user_id=user_id,
            watch_duration_seconds=watch_duration_seconds,
            completion_percentage=completion_percentage,
            playback_speed=playback_speed,
            quality_selected=quality_selected,
            device_type=device_type
        )
        
        db.add(analytics)
        await db.commit()
        await db.refresh(analytics)
        
        return analytics
    
    async def get_video_analytics(
        self,
        db: AsyncSession,
        lesson_id: UUID
    ) -> Dict[str, Any]:
        """Get aggregated video analytics for a lesson"""
        from sqlalchemy import func
        
        result = await db.execute(
            select(
                func.count(VideoAnalytics.id).label('total_views'),
                func.avg(VideoAnalytics.completion_percentage).label('avg_completion'),
                func.avg(VideoAnalytics.watch_duration_seconds).label('avg_watch_time'),
                func.count(func.distinct(VideoAnalytics.user_id)).label('unique_viewers')
            )
            .where(VideoAnalytics.lesson_id == lesson_id)
        )
        
        row = result.first()
        
        return {
            "total_views": row.total_views or 0,
            "avg_completion_percentage": float(row.avg_completion or 0),
            "avg_watch_time_seconds": int(row.avg_watch_time or 0),
            "unique_viewers": row.unique_viewers or 0
        }
