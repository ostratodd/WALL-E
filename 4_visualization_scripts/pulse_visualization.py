#Visualization options to be programmed
#Visualize after removing noise
#print(finalpulses.to_string())

#fig, axs = plt.subplots(ncols=2)
#sns.scatterplot(x='frame', y='cX', data=denoised, hue='pulse', edgecolor = 'none', ax=axs[0], legend = True)
#axs[0].set_ylim(1, 640)
#sns.scatterplot(x='frame', y='cY', data=denoised, hue='pulse', edgecolor = 'none', ax=axs[1], legend = False)
#axs[1].set_ylim(1, 480)

#Compare raw L/R camera data to inferred stereo pulses
maxframes = finalpulses['frame'].max()
fig, axs = plt.subplots(ncols=2)
sns.scatterplot(x='frame', y='cY', data=finalpulses, hue='camera', edgecolor = 'none', ax=axs[0], s=10, legend = True).set(title='Raw contour data by camera')
axs[0].set_ylim(1, 480)
axs[0].set_xlim(1, maxframes)
axs[0].set_xlabel('Time (video frames)')

sns.set_palette("bright")
sns.scatterplot(x='start', y='modey', data=df_stereo_pairs, hue='spulse', edgecolor = 'none', ax=axs[1], s=50, legend = True).set(title='Algorithmically inferred stereo pulses')
axs[1].set_ylim(1, 480)
axs[1].set_xlim(1, maxframes)
axs[1].set_xlabel('Start of Stereo Pulse (frame)')

#fig, axs = plt.subplots()
#sns.scatterplot(x='start', y='modey', data=df_stereo_pairs, hue='spulse', edgecolor = 'none', ax=axs, legend = True)
#axs.set_ylim(1, 640)
#axs.set_xlim(1, 480)

##3d stereopolot
#plt.figure(figsize=(6,5))
#axes = plt.axes(projection='3d')
#print(type(axes))
#axes.scatter3D(df_stereo_pairs['start'], df_stereo_pairs['minx'], df_stereo_pairs['modey'], s=10)
#axes.set_xlabel('time')
#axes.set_ylabel('x position')
#axes.set_zlabel('y position')



#sns.scatterplot(x='frame', y='cX', data=noise, edgecolor = 'black', ax=axs[0], legend = False)

plt.show()