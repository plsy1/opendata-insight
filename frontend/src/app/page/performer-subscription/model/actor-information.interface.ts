export interface SocialMedia {
  platform: string;
  username: string;
  link: string;
}

export interface ActorSubscription {
  actor_id: number;
  is_subscribe: boolean;
  is_collect: boolean;
  subscribe_order: number;
  collect_order: number;
  created_at?: string | null;
}

export interface ActorProfile {
  name: string;
  birthday: string | null;
  height: string | null;
  bust: string | null;
  waist: string | null;
  hip: string | null;
  cup: string | null;
  prefectures: string | null;
  hobby: string | null;
  blood_type: string | null;
  aliases: string[];
  avatar_url: string | null;
  social_media: SocialMedia[];
  ruby?: string | null;
  updated_at?: string | null;
  subscribers?: ActorSubscription | null;
  [key: string]: unknown;
}

export interface Actress extends ActorProfile {
  id: number;
  raw_avatar_url?: string;
  isCollect?: boolean;
  isSubscribe?: boolean;
}
