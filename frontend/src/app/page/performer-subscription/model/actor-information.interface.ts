export interface SocialMedia {
  platform: string;
  username: string;
  link: string;
}

export interface Actress {
  id: number;
  name: string;
  birthday: string | null;
  height: string;
  bust: string;
  waist: string;
  hip: string;
  cup: string;
  prefectures: string;
  hobby: string;
  blood_type: string | null;
  aliases: string[];
  avatar_url: string;
  social_media: SocialMedia[];
  raw_avatar_url?: string;
  isCollect: boolean;
  isSubscribe: boolean;
}