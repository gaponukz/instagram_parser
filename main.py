from requests import get
from bs4 import BeautifulSoup
from json import loads, dumps, dump

class User:
	def __init__(self, username: str, write: bool = False):
		self.write_in_file = write
		self.username = username
		self.response = get(f'https://instagram.com/{self.username}')

		if self.response.status_code == 200:
			self.soup = BeautifulSoup(self.response.text, 'html.parser')
			scripts = self.soup.find_all('script')
			data_script = scripts[4]
			# find data
			content = data_script.contents[0]
			data_object = content[content.find('{"config"') : -1]
			data_json = loads(data_object)
			self.data_json = data_json['entry_data']['ProfilePage'][0]['graphql']['user']

			if self.write_in_file:
				with open('data.json', 'w', encoding = 'utf-8') as file:
					dump(self.data_json, file, ensure_ascii = False, indent = 4)
			
			self.biography = self.data_json['biography']
			self.followers = int(self.data_json['edge_followed_by']['count'])
			self.following = int(self.data_json['edge_follow']['count'])
			self.full_name = self.data_json['full_name']
			self.external_url = self.data_json['external_url']
			self.icon_url = self.data_json['profile_pic_url_hd']
			self.category_enum = self.data_json['category_enum']
			self.is_private = bool(self.data_json['is_private'])
			self.total_posts_count = int(self.data_json['edge_owner_to_timeline_media']['count'])

	def get_posts(self):
		posts = []

		for i in range(len(self.data_json['edge_owner_to_timeline_media']['edges'])):
			post = self.data_json['edge_owner_to_timeline_media']['edges'][i]
			if not post['node']['is_video']:
				height = post['node']['dimensions']['height']
				width = post['node']['dimensions']['width']
				print(f"Photo {height}x{width}")

			posts.append(post['node']['display_url'])
			print(f"Url: {post['node']['display_url']}")
			print(f"Likes: {post['node']['edge_liked_by']['count']}\n")

			try: post['node']['edge_sidecar_to_children']
			except: pass
			else:
				for j in range(len(post['node']['edge_sidecar_to_children']['edges'])):
					child_post = post['node']['edge_sidecar_to_children']['edges'][j]
					posts.append(child_post['node']['display_url'])
					if not post['node']['is_video']:
						height = child_post['node']['dimensions']['height']
						width = child_post['node']['dimensions']['width']
						print(f"Photo {height}x{width}")

					print(child_post['node']['display_url'], '\n')

		return posts

if __name__ == '__main__':
	user = User('__zhenyagaponyuk')

	print(f"Information for {user.username}")
	print(f"Biography:\n'{user.biography}'")
	print(f"Followers: {user.followers}")
	print(f"Following: {user.following}")
	print(f"User have {'private' if user.is_private else 'publick'} account")
	print(f"User have {user.total_posts_count} posts")
	user.get_posts()
