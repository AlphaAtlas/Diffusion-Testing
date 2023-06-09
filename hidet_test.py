from diffusers import StableDiffusionPipeline
import torch
import torch._dynamo
import hidet

#Create pipeline
#Change path to a remote model
pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
pipe = pipe.to("cuda")

#Typical diffusers pipeline optimizations
print("### Pre Optimization Benchmark:")
image = pipe("a photo of an astronaut riding a horse on mars").images[0]

pipe.unet.to(memory_format=torch.channels_last) #Unsupported by hidet, but does not seem to make a difference if disabled.
pipe.enable_vae_tiling()
pipe.enable_xformers_memory_efficient_attention()

print("### Post optimization benchmark:")
image = pipe("a photo of an astronaut riding a horse on mars").images[0]



#Set compile
torch._dynamo.config.suppress_errors = True
# more search 
hidet.torch.dynamo_config.search_space(2)
# automatically transform the model to use float16 data type
hidet.torch.dynamo_config.use_fp16(True)
# use float16 data type as the accumulate data type in operators with reduction
hidet.torch.dynamo_config.use_fp16_reduction(True)
# use tensorcore
hidet.torch.dynamo_config.use_tensor_core()
pipe.unet = torch.compile(pipe.unet, backend="hidet")

print("### torch.compile warmup:")
image = pipe("a photo of an astronaut riding a horse on mars").images[0]

print("torch.compile benchmark:")
image = pipe("a photo of an astronaut riding a horse on mars").images[0]




