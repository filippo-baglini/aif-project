def _process_obs(env, agent_vis_mask, agent_vis_obs):
        """Parse the contents of an observation/image, update our state,
        rotate the vis_mask to the right, and make it specular."""

        obs_grid, vis_mask = env.unwrapped.gen_obs_grid()

        view_size = env.unwrapped.agent_view_size
        pos = env.unwrapped.agent_pos
        f_vec = env.unwrapped.dir_vec
        r_vec = env.unwrapped.right_vec

        # Compute the absolute coordinates of the top-left corner
        # of the agent's view area
        top_left = pos + f_vec * (view_size - 1) - r_vec * (view_size // 2)

        # Mark everything in front of us as visible
        for vis_j in range(0, view_size):
            for vis_i in range(0, view_size):
                if not vis_mask[vis_i, vis_j]:
                    continue

                # Compute the world coordinates of this cell
                abs_i, abs_j = top_left - (f_vec * vis_j) + (r_vec * vis_i)

                if abs_i < 0 or abs_i >= agent_vis_mask.shape[0]:
                    continue
                if abs_j < 0 or abs_j >= agent_vis_mask.shape[1]:
                    continue

                agent_vis_mask[abs_i, abs_j] = True
                # self.vis_type [abs_i, abs_j]
                
                if obs_grid.get(vis_i, vis_j) == None:
                    agent_vis_obs[abs_i, abs_j] = 1
                else:
                    agent_vis_obs[abs_i, abs_j] = obs_grid.get(vis_i, vis_j).encode()
                # print(obj)

        rotated_mask = agent_vis_mask.T[:, ::-1]
        specular_mask = rotated_mask[:, ::-1] #for visual debugging vis_mask

        rotated_obs = agent_vis_obs.T[:, ::-1]
        specular_obs = rotated_obs[:, ::-1] #for visual debugging vis_obs

        return agent_vis_mask, agent_vis_obs

