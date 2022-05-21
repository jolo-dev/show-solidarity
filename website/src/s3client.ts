import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3'

const region = import.meta.env.VITE_AWS_REGION ?? 'eu-central-1';
const accessKeyId = import.meta.env.VITE_AWS_ACCESS_KEY_ID;
const secretAccessKey = import.meta.env.VITE_AWS_SECRET_ACCESS_KEY;
const sessionToken = import.meta.env.VITE_AWS_SESSION_TOKEN;


const s3 = new S3Client({region, credentials: {
    accessKeyId,
    secretAccessKey,
    sessionToken
}})


export async function uploadImage(Bucket:string, Key: string, Body: Blob){
    const uploadedImage = await s3.send(new PutObjectCommand({ Bucket, Key, Body }))
    return uploadedImage;
}
